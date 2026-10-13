"""Freeze renderer source while keeping installed dependencies local."""
import os
from pathlib import Path
import shutil
import subprocess


def snapshot_browser_project(spec,base_dir,output_dir,snapshots):
    original=(Path(base_dir)/spec['project_dir']).resolve()
    entry=(original/spec['entry_point']).resolve()
    if not entry.is_relative_to(original) or not entry.is_file():
        raise ValueError('Renderer entry point must be inside project_dir')
    if original not in snapshots:
        target=Path(output_dir)/'renderer_projects'/f'project_{len(snapshots)+1}'
        shutil.copytree(original,target,ignore=shutil.ignore_patterns('node_modules','out','dist','build','.git','.cache','.env','.env.*','*.key','*.log'))
        dependencies=original/'node_modules'
        if not dependencies.is_dir(): raise RuntimeError(f'Install renderer dependencies with npm ci in {original}')
        link=target/'node_modules'
        if os.name=='nt':
            subprocess.run(['cmd','/c','mklink','/J',str(link),str(dependencies)],check=True,capture_output=True)
        else: link.symlink_to(dependencies,target_is_directory=True)
        snapshots[original]=target
    spec['project_dir']=str(snapshots[original])
