curl -L https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz -o /usr/local/bin/ffmpeg.tar.xz
cd /usr/local/bin/
7z e /usr/local/bin/ffmpeg.tar.xz
7z e /usr/local/bin/ffmpeg.tar
chmod a+rx /usr/local/bin/ffmpeg
cd /content/
curl -L https://mkvtoolnix.download/appimage/MKVToolNix_GUI-70.0.0-x86_64.AppImage -o /usr/local/bin/MKVToolNix_GUI-70.0.0-x86_64.AppImage
chmod u+rx /usr/local/bin/MKVToolNix_GUI-70.0.0-x86_64.AppImage
ln -s /usr/local/bin/MKVToolNix_GUI-70.0.0-x86_64.AppImage /usr/local/bin/mkvmerge
chmod a+rx /usr/local/bin/mkvmerge
ffmpeg -version