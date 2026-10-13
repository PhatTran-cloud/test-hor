"""Local green-screen matte; preserves source and leaves edge review unverified."""
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image


def chroma_key(source,output,inner=30,outer=100,despill=True):
    from v4_contract import sha256
    source=Path(source).resolve(); output=Path(output).resolve()
    mask_file=output.with_suffix('.mask.png'); receipt_file=output.with_suffix('.chroma.json')
    if output.suffix.lower()!='.png': raise ValueError('Keyed cutouts require alpha PNG output')
    targets=[output,mask_file,receipt_file]
    if source in targets: raise ValueError('Preserve the source; choose a distinct output path')
    if any(p.exists() for p in targets): raise FileExistsError('Choose new output names; originals/results are not overwritten')
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in [inner,outer]) or not 0<=inner<outer<255:
        raise ValueError('Use finite 0 <= inner < outer < 255 RGB distance thresholds')
    source_hash=sha256(source)
    with Image.open(source) as image:
        rgba=np.asarray(image.convert('RGBA'),dtype=np.float32).copy()
    rgb=rgba[:,:,:3]; original_alpha=rgba[:,:,3]/255
    distance=np.linalg.norm(rgb-np.array([0,255,0],dtype=np.float32),axis=2)
    matte=np.clip((distance-inner)/(outer-inner),0,1)
    removed=(matte==0)&(original_alpha>0)
    if not removed.any(): raise ValueError('No removable solid green background found; inspect the source/thresholds')
    alpha=np.rint(matte*original_alpha*255).astype(np.uint8)
    if not (alpha>0).any(): raise ValueError('Key removed the entire subject; no usable cutout')
    if despill:
        edge=(matte>0)&(matte<1)
        green=rgb[:,:,1]
        green[edge]=np.minimum(green[edge],np.maximum(rgb[:,:,0],rgb[:,:,2])[edge])
    rgba[:,:,:3][alpha==0]=0
    rgba[:,:,3]=alpha
    if sha256(source)!=source_hash: raise ValueError('Source changed during chroma key processing')
    output.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(np.rint(rgba).astype(np.uint8)).save(output)
    Image.fromarray(alpha).save(mask_file)
    receipt={'source':str(source),'source_sha256':source_hash,'output':str(output),
        'output_sha256':sha256(output),'mask':str(mask_file),'mask_sha256':sha256(mask_file),
        'key_color':'#00FF00','algorithm':'rgb_distance_soft_matte_v1',
        'parameters':{'inner':inner,'outer':outer,'despill':despill},
        'width':rgba.shape[1],'height':rgba.shape[0],
        'transparent_pixels':int((alpha==0).sum()),'partial_alpha_pixels':int(((alpha>0)&(alpha<255)).sum()),
        'opaque_pixels':int((alpha==255).sum()),'review':{'status':'UNVERIFIED',
            'required':'Inspect hair/thin limbs/holes/crop and halos on light and dark backgrounds; green subject colors cannot be recovered by this key.'}}
    receipt_file.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    return receipt
