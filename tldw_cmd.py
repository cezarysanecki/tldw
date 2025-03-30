import sys
from tldw import summarize_video

url = sys.argv[1]

summarize = summarize_video(url)

print(summarize)
