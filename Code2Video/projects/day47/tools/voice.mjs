import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {readFile, writeFile, mkdir, access, rename, rm} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {CUES, SCRIPT, VIDEO, VOICE, assertScriptSegmentation} from '../src/script.mjs';

export const PROJECT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const OUTPUT = path.resolve(PROJECT, '../../..', 'outputs/day47');
export const run = promisify(execFile);
export const hash = value => createHash('sha256').update(value).digest('hex');
const exists = async file => {try {await access(file); return true;} catch {return false;}};
const clock = value => {const [h, m, s] = value.replace(',', '.').split(':').map(Number); return h * 3600 + m * 60 + s;};

export function parseSrt(text) {
  return text.trim().split(/\r?\n\s*\r?\n/).filter(Boolean).map(block => {
    const lines = block.split(/\r?\n/), pair = lines[1]?.split(' --> ');
    if (!pair || pair.length !== 2) throw new Error('Malformed Edge TTS boundary file');
    return {start: clock(pair[0]), end: clock(pair[1]), text: lines.slice(2).join(' ')};
  });
}

export function pcmData(buffer) {
  if (buffer.toString('ascii', 0, 4) !== 'RIFF' || buffer.toString('ascii', 8, 12) !== 'WAVE') throw new Error('Expected PCM WAV');
  let data, format;
  for (let p = 12; p + 8 <= buffer.length;) {
    const id = buffer.toString('ascii', p, p + 4), size = buffer.readUInt32LE(p + 4);
    if (id === 'fmt ') format = {encoding: buffer.readUInt16LE(p + 8), channels: buffer.readUInt16LE(p + 10), rate: buffer.readUInt32LE(p + 12), bits: buffer.readUInt16LE(p + 22)};
    if (id === 'data') data = buffer.subarray(p + 8, p + 8 + size);
    p += 8 + size + (size % 2);
  }
  if (!data || format?.encoding !== 1 || format?.channels !== 1 || format?.rate !== VIDEO.sampleRate || format?.bits !== 16) throw new Error('Expected mono PCM16 48 kHz');
  return data;
}

export function wave(data) {
  const header = Buffer.alloc(44);
  header.write('RIFF'); header.writeUInt32LE(data.length + 36, 4); header.write('WAVEfmt ', 8);
  header.writeUInt32LE(16, 16); header.writeUInt16LE(1, 20); header.writeUInt16LE(1, 22);
  header.writeUInt32LE(VIDEO.sampleRate, 24); header.writeUInt32LE(VIDEO.sampleRate * 2, 28);
  header.writeUInt16LE(2, 32); header.writeUInt16LE(16, 34); header.write('data', 36); header.writeUInt32LE(data.length, 40);
  return Buffer.concat([header, data]);
}

export async function prepareVoice() {
  assertScriptSegmentation();
  const dir = path.join(OUTPUT, 'voice'); await mkdir(dir, {recursive: true});
  const samplesPerFrame = VIDEO.sampleRate / VIDEO.fps;
  const pieces = [Buffer.alloc(VIDEO.leadFrames * samplesPerFrame * 2)];
  const utterances = []; let frame = VIDEO.leadFrames;
  for (const cue of CUES) {
    const requestHash = hash(JSON.stringify({text: cue.text, ...VOICE}));
    const stem = path.join(dir, cue.id), mp3 = stem + '.mp3', srt = stem + '.srt', wav = stem + '.wav', receipt = stem + '.json';
    let cached;
    if (await exists(receipt)) cached = JSON.parse(await readFile(receipt, 'utf8'));
    if (!cached || cached.request_sha256 !== requestHash || !(await exists(mp3)) || hash(await readFile(mp3)) !== cached.mp3_sha256 || !(await exists(srt)) || hash(await readFile(srt)) !== cached.boundaries_sha256) {
      console.log(`Edge TTS ${cue.id}: ${cue.text}`);
      const tempMp3 = mp3 + '.pending', tempSrt = srt + '.pending';
      const args = ['--voice', VOICE.name, `--rate=${VOICE.rate}`, `--pitch=${VOICE.pitch}`, `--volume=${VOICE.volume}`, '--text', cue.text, '--write-media', tempMp3, '--write-subtitles', tempSrt, '--no-progress'];
      try {
        // Optional Python module invocation is only the Edge service client.
        // Storyboard, timing, drawings and both renderer adapters are JavaScript.
        if (process.env.EDGE_TTS_PYTHON) await run(process.env.EDGE_TTS_PYTHON, ['-m', 'edge_tts', ...args], {timeout: 90000, maxBuffer: 2 ** 20});
        else await run(process.env.EDGE_TTS_BIN || 'edge-tts', args, {timeout: 90000, maxBuffer: 2 ** 20});
        await run('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'json', tempMp3]);
        await rename(tempMp3, mp3); await rename(tempSrt, srt);
      } catch (error) {
        await rm(tempMp3, {force: true}); await rm(tempSrt, {force: true});
        throw new Error(`Edge TTS failed at ${cue.id}; no estimated or silent VO substituted. ${error.message}`);
      }
    } else console.log(`Cached measured take ${cue.id}`);
    await run('ffmpeg', ['-v', 'error', '-y', '-i', mp3, '-ar', String(VIDEO.sampleRate), '-ac', '1', '-c:a', 'pcm_s16le', wav]);
    const audio = pcmData(await readFile(wav)), samples = audio.length / 2;
    const frames = Math.ceil(samples / samplesPerFrame), pauseFrames = Math.round(cue.pauseAfter * VIDEO.fps);
    const boundaries = parseSrt(await readFile(srt, 'utf8'));
    if (!samples || !boundaries.length || boundaries.some(b => b.end > samples / VIDEO.sampleRate + .15 || b.end <= b.start)) throw new Error(`Invalid measured take or boundary metadata: ${cue.id}`);
    const take = {
      id: cue.id, text: cue.text, start_frame: frame, end_frame: frame + frames,
      start_sample: frame * samplesPerFrame, end_sample: frame * samplesPerFrame + samples,
      sample_count: samples, duration_seconds: samples / VIDEO.sampleRate, padding_samples: frames * samplesPerFrame - samples,
      pause_frames: pauseFrames, confidence: 'measured_segment',
      mp3: `voice/${cue.id}.mp3`, mp3_sha256: hash(await readFile(mp3)), pcm_sha256: hash(audio),
      request_sha256: requestHash, boundaries_sha256: hash(await readFile(srt)), boundaries,
      listening_review: 'UNVERIFIED',
    };
    await writeFile(receipt, JSON.stringify(take, null, 2) + '\n');
    pieces.push(audio, Buffer.alloc((take.padding_samples + pauseFrames * samplesPerFrame) * 2));
    utterances.push(take); frame += frames + pauseFrames;
  }
  const buffer = wave(Buffer.concat(pieces));
  await writeFile(path.join(OUTPUT, 'narration.wav'), buffer);
  const timeline = {
    schema: 'day47/measured-voice/1', ...VIDEO, voice: VOICE, script_sha256: hash(SCRIPT),
    audio_file: 'narration.wav', audio_sha256: hash(buffer), audio_samples: (buffer.length - 44) / 2,
    frames: frame, duration_seconds: frame / VIDEO.fps, time_stretch: false,
    timing_basis: 'Decoded PCM samples at 48000 Hz, padded to 60 fps; boundaries are Edge metadata, not listening verification',
    utterances,
    listening_review: 'UNVERIFIED',
  };
  await writeFile(path.join(OUTPUT, 'voice-timing.json'), JSON.stringify(timeline, null, 2) + '\n');
  console.log(`Measured voice timeline: ${timeline.duration_seconds.toFixed(3)} s / ${frame} frames`);
  return timeline;
}
