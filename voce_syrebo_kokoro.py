import os,subprocess,urllib.request,json
from pathlib import Path
import umpy as p
import soundfile as sf
from kokoro import KPipeline
VIDEO_URL="https://static.metricool.com/planner/202611/7090850-file-2427182708283205949.mp4"
SCRIPT="[VOCE](/ˈvotʃe/) explores rehabilitation robotics for people recovering movement. Syrebo hand therapy systems need careful evaluation of outcomes, therapist training, and maintenance. Technology should always serve patients. [VOCE](/ˈvotʃe/). No one left unheard."
out=Path("VOCE_Syrebo_Kokoro_Votche.mp4")
audio=Path("VOCE_Syrebo_Kokoro_Votche_Narration.wav")
video=Path("voce_syrebo_source.mp4")
urllib.request.urlretrieve(VIDEO_URL,video)
if video.stat().st_size&lt;10000: raise RuntimeError("Source video failed")
pipeline=KPipeline(lang_code="a")
clips=[]
for _,_,wave in pipeline(SCRIPT,voice="af_heart",speed=0.85):
    if wave is not None: clips.append( p.asarray(wave,dtype=np.float32).reshape(-1))
if not clips: raise RuntimeError("Kokoro generated no audio")
sf.write(str(audio),np.concatenate(clips),24000)
def duration(path):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)],text=True).strip())
length=max(duration(video),duration(audio)+0.7)
subprocess.run(["ffmpeg","-y","-i",str(video),"-i",str(audio),"-filter_complex","[0:v:0]tpad=stop_mode=clone:stop_duration=100,format=yuv420p[v]","-map","[v]","-map","1:a:0","-c:v","libx264","-preset","veryfast","-crf","22","-c:a","aac","-b:a","160k","-af","apad","-t",f"{length:.2f}","-movflags","+faststart",str(out)],check=True)
if out.stat().st_size&lt;30000: raise RuntimeError("Rendered MP4 invalid")
print("VOCE Syrebo rendered:",out,"seconds",duration(out))
