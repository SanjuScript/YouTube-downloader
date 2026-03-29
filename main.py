#!/usr/bin/env python3
"""
YouTube Video / Audio Downloader
Uses: yt-dlp (up-to-date as of 2026)

Install dependencies:
    pip install yt-dlp
    # Also install ffmpeg (required for merging video+audio and audio conversion)
    # macOS:   brew install ffmpeg
    # Ubuntu:  sudo apt install ffmpeg
    # Windows: https://ffmpeg.org/download.html
"""

import yt_dlp
import os
import sys


DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "YT_Downloads")


def progress_hook(d):
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "?%").strip()
        speed = d.get("_speed_str", "?").strip()
        eta = d.get("_eta_str", "?").strip()
        print(f"\r  Downloading: {percent}  Speed: {speed}  ETA: {eta}    ", end="", flush=True)
    elif d["status"] == "finished":
        print(f"\n  ✅ Download complete → {d['filename']}")
    elif d["status"] == "error":
        print(f"\n  ❌ Error during download.")


def get_video_opts(quality: str) -> dict:
    """Returns yt-dlp options for video download."""
    format_map = {
        "1": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best[height<=480]",
        "2": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]",
        "3": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "4": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
    }
    fmt = format_map.get(quality, "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best")

    return {
        "format": fmt,
        "merge_output_format": "mp4",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "progress_hooks": [progress_hook],
        "ffmpeg_location": "/opt/homebrew/bin/ffmpeg",
        "postprocessors": [
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }
        ],
        "noplaylist": True,
        "quiet": True,
        "no_warnings": False,
    }


def get_audio_opts(fmt: str) -> dict:
    """Returns yt-dlp options for audio-only download."""
    return {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "ffmpeg_location": "/opt/homebrew/bin/ffmpeg",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": fmt,
                "preferredquality": "0",
            }
        ],
        "progress_hooks": [progress_hook],
        "noplaylist": True,
        "quiet": True,
        "no_warnings": False,
    }


def fetch_info(url: str) -> dict | None:
    """Fetches video metadata without downloading."""
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "noplaylist": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except yt_dlp.utils.DownloadError as e:
        print(f"  ❌ Could not fetch video info: {e}")
        return None


def print_info(info: dict):
    print(f"\n  Title     : {info.get('title', 'Unknown')}")
    print(f"  Channel   : {info.get('uploader', 'Unknown')}")
    duration  = info.get("duration", 0)
    mins, secs = divmod(duration, 60)
    print(f"  Duration  : {mins}m {secs}s")
    print(f"  Views     : {info.get('view_count', 0):,}")


def download(url: str, opts: dict):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        print(f"\n  ❌ Download failed: {e}")
        print("  Tip: Run `pip install -U yt-dlp` to update and try again.")
        sys.exit(1)


def main():
    print("=" * 50)
    print("    YouTube Downloader  |  Powered by yt-dlp")
    print("=" * 50)

    url = input("\n  Paste YouTube URL: ").strip()
    if not url:
        print("  ❌ No URL provided.")
        sys.exit(1)

    print("\n  Fetching video info...")
    info = fetch_info(url)
    if not info:
        sys.exit(1)

    print_info(info)

    print("\n  What do you want to download?")
    print("  [1] Video")
    print("  [2] Audio only")
    mode = input("\n  Choose (1/2): ").strip()

    if mode == "1":
        print("\n  Select video quality:")
        print("  [1] 480p")
        print("  [2] 720p")
        print("  [3] 1080p")
        print("  [4] Best available")
        quality = input("\n  Choose (1-4): ").strip()
        opts = get_video_opts(quality)

    elif mode == "2":
        print("\n  Select audio format:")
        print("  [1] mp3")
        print("  [2] m4a")
        print("  [3] opus")
        print("  [4] flac")
        print("  [5] wav")
        fmt_map = {"1": "mp3", "2": "m4a", "3": "opus", "4": "flac", "5": "wav"}
        fmt_choice = input("\n  Choose (1-5): ").strip()
        audio_fmt = fmt_map.get(fmt_choice, "mp3")
        opts = get_audio_opts(audio_fmt)

    else:
        print("  ❌ Invalid choice.")
        sys.exit(1)

    print(f"\n  Starting download → {DOWNLOAD_DIR}\n")
    download(url, opts)
    print(f"\n  Saved to: {DOWNLOAD_DIR}")
    print("=" * 50)


if __name__ == "__main__":
    main()