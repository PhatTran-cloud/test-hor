// Use the installed project's pinned Remotion runtime; retain browser observations.
// No packages are installed, no source is generated, and no LLM is invoked.
const fs = require('node:fs');
const path = require('node:path');
const {createRequire} = require('node:module');

async function main() {
  const [project, entry, compositionId, propsFile, output] = process.argv.slice(2);
  const projectRequire = createRequire(path.join(project, 'package.json'));
  const {bundle} = projectRequire('@remotion/bundler');
  const {selectComposition, renderMedia} = projectRequire('@remotion/renderer');
  const props = JSON.parse(fs.readFileSync(propsFile, 'utf8'));
  const onBrowserLog = ({text, type}) => {
    if (text.includes('V4_EXECUTION_SAMPLE ')) process.stdout.write(text + '\n');
    if (type === 'error') process.stderr.write(text + '\n');
  };
  const serveUrl = await bundle({entryPoint: path.resolve(project, entry)});
  const chromiumOptions = {gl: 'angle'};
  // Metadata evaluation uses a temporary viewport, not the delivery frame.
  // Only actual rendering may emit delivery-space execution observations.
  const metadataProps = {...props, productionContract: {...props.productionContract, metadata_only: true}};
  const composition = await selectComposition({serveUrl, id: compositionId, inputProps: metadataProps, chromiumOptions});
  if (composition.width !== 1920 || composition.height !== 1080 || composition.fps !== 60 || composition.durationInFrames !== props.durationInFrames)
    throw new Error('Composition did not honor the 1080p60 authored frame allocation');
  // selectComposition returns its evaluated props as composition.props.
  // Restore the actual production props, including normal runtime auditing.
  const renderComposition = {...composition, props: {...composition.props, ...props}};
  await renderMedia({serveUrl, composition: renderComposition, inputProps: props, outputLocation: output,
    codec: 'h264', pixelFormat: 'yuv420p', muted: true, concurrency: 2, chromiumOptions, onBrowserLog});
}
main().catch((error) => {console.error(error); process.exitCode = 1;});
