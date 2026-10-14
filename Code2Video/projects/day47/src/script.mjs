// Source text is locked to the user's 14 October 2026 request.
export const SCRIPT = `Ngày 47, tôi nhận được câu trả lời cho câu hỏi tôi chưa kịp hỏi. Nó ở cách tôi 600.000km. Nghĩa là... nó ở ngay sau lưng trạm.

Vũ trụ không bao giờ thực sự im lặng. Nó chỉ đang nín thở để nghe lén mày.

Tôi bắn 3 tiếng HELLO về phía sao Mộc. 4 giây sau, nó trả lời. Ngôi sao gần nhất cách 4 năm ánh sáng. Vậy thứ trả lời tôi... cách tôi 600.000km.

Tôi tưởng đó là đá. Đến khi cả vành đai cùng co lại một lúc, tôi mới hiểu. Tôi đang bay trong mắt của nó.

Einstein nói đúng. Trọng lực bẻ cong ánh sáng. Nhưng ông không nói... khi mày nhìn vào chỗ cong đó đủ lâu, chỗ cong đó cũng nhìn lại mày.

Tôi chớp mắt. Và trạm cũng chớp mắt cùng tôi.

Nếu mày nghe thấy tín hiệu này, đừng trả lời. Vì 47 ngày trước, tao cũng nghĩ như mày. Và giờ tao là thứ đang gõ cửa trạm mày.`;

const texts = [
  'Ngày 47, tôi nhận được câu trả lời cho câu hỏi tôi chưa kịp hỏi.',
  'Nó ở cách tôi 600.000km.',
  'Nghĩa là... nó ở ngay sau lưng trạm.',
  'Vũ trụ không bao giờ thực sự im lặng.',
  'Nó chỉ đang nín thở để nghe lén mày.',
  'Tôi bắn 3 tiếng HELLO về phía sao Mộc.',
  '4 giây sau, nó trả lời.',
  'Ngôi sao gần nhất cách 4 năm ánh sáng.',
  'Vậy thứ trả lời tôi... cách tôi 600.000km.',
  'Tôi tưởng đó là đá.',
  'Đến khi cả vành đai cùng co lại một lúc, tôi mới hiểu.',
  'Tôi đang bay trong mắt của nó.',
  'Einstein nói đúng.',
  'Trọng lực bẻ cong ánh sáng.',
  'Nhưng ông không nói... khi mày nhìn vào chỗ cong đó đủ lâu, chỗ cong đó cũng nhìn lại mày.',
  'Tôi chớp mắt.',
  'Và trạm cũng chớp mắt cùng tôi.',
  'Nếu mày nghe thấy tín hiệu này, đừng trả lời.',
  'Vì 47 ngày trước, tao cũng nghĩ như mày.',
  'Và giờ tao là thứ đang gõ cửa trạm mày.',
];
const pauses = [.5, .45, 1.25, .5, 1.1, 4, .65, .45, 1.1, .7, .75, 1.5, .25, .6, 1.1, .2, 1.25, .8, .65, 2.4];
export const CUES = texts.map((text, i) => ({id: `vo_${String(i + 1).padStart(2, '0')}`, text, pauseAfter: pauses[i]}));
export function assertScriptSegmentation(script=SCRIPT,cues=CUES) {
  if(cues.map(c=>c.text).join(' ')!==script.replace(/\s+/g,' '))throw new Error('Narration segments differ from SCRIPT; update SCRIPT and CUES together before generating voice');
}
export const VOICE = {provider: 'edge-tts', version: '7.3.1', name: 'vi-VN-NamMinhNeural', rate: '-8%', pitch: '-6Hz', volume: '+0%'};
export const VIDEO = {width: 1920, height: 1080, fps: 60, sampleRate: 48000, leadFrames: 72};
export const USER_OVERRIDE = {
  date: '2026-10-14', scope: 'day47 voiced storyboard only',
  instruction: 'dùng edgetts cho voi tự căn timeline, chỉ dùng js + remotion + hyperframes vẽ cho đại ca',
  narration: 'Edge TTS; one Vietnamese narrator; measured takes; no time stretching',
  illustration: 'Original editable JavaScript/SVG drawings shared by Remotion and Hyperframes',
  sound: 'Voice only; authored digital silence; no music requested',
  review: 'Storyboard animatic for review; no automatic final-film approval',
};
