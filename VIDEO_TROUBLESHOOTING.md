# 🎥 Video Troubleshooting Guide

## Common Issues & Solutions

### Issue 1: Video Not Showing

#### Symptoms:
- Black screen where video should be
- "Camera is off" message appears
- Video element is blank

#### Solutions:

**1. Check Browser Permissions**
```
Chrome/Edge:
1. Click the 🔒 icon in address bar
2. Check Camera is set to "Allow"
3. Check Microphone is set to "Allow"
4. Refresh the page
```

**2. Check if Camera is in Use**
- Close other apps using camera (Zoom, Teams, etc.)
- Close other browser tabs with camera access
- Restart browser

**3. Use Correct Browser**
- ✅ Chrome 90+ (Best)
- ✅ Edge 90+ (Best)
- ⚠️ Safari (Limited support)
- ⚠️ Firefox (Limited support)

**4. Check Camera Hardware**
```bash
# On Mac, check camera status:
# System Preferences → Security & Privacy → Camera

# On Windows:
# Settings → Privacy → Camera
```

**5. Try HTTPS Instead of HTTP**
Some browsers require HTTPS for camera access:
```
https://localhost:3000/interviews/ai-video/demo-123
```

---

### Issue 2: Mute Button Not Working

#### What Was Fixed:
- ✅ Toggle functions now properly control audio tracks
- ✅ Visual feedback shows mute state
- ✅ Red background when muted

#### How It Works Now:
```typescript
// Mute button toggles the audio track
toggleMicrophone() {
  audioTrack.enabled = !audioTrack.enabled
  setMicEnabled(audioTrack.enabled)
}
```

#### To Test:
1. Start interview
2. Click microphone button
3. Button turns red when muted
4. Click again to unmute

---

### Issue 3: Camera Button Not Working

#### What Was Fixed:
- ✅ Toggle functions now properly control video tracks
- ✅ "Camera is off" overlay shows when disabled
- ✅ Red background when camera off

#### How It Works Now:
```typescript
// Camera button toggles the video track
toggleCamera() {
  videoTrack.enabled = !videoTrack.enabled
  setCameraEnabled(videoTrack.enabled)
}
```

#### To Test:
1. Start interview
2. Click camera button
3. Video hides and shows "Camera is off"
4. Button turns red when off
5. Click again to turn on

---

### Issue 4: Video Appears But Frozen

#### Solutions:

**1. Check Frame Rate**
The video should be requesting 720p at 30fps:
```typescript
video: {
  width: { ideal: 1280 },
  height: { ideal: 720 },
  facingMode: 'user'
}
```

**2. Restart Stream**
1. Click "End Interview"
2. Start a new interview
3. Allow permissions again

**3. Check System Resources**
- Close unnecessary apps
- Check CPU usage
- Ensure good lighting

---

### Issue 5: Permission Denied Error

#### Error Message:
```
"Please allow camera and microphone access to continue with the interview."
```

#### Solutions:

**1. Reset Browser Permissions**
```
Chrome:
1. Go to chrome://settings/content/camera
2. Remove localhost from blocked list
3. Refresh page and allow again
```

**2. Check System Permissions**
```
Mac:
System Preferences → Security & Privacy → Camera
- Ensure browser is checked

Windows:
Settings → Privacy → Camera
- Ensure browser has access
```

**3. Try Incognito/Private Mode**
- Open incognito window
- Navigate to interview page
- Allow permissions when prompted

---

## Testing Checklist

### Before Starting Interview:
- [ ] Using Chrome or Edge browser
- [ ] Camera is connected and working
- [ ] Microphone is connected and working
- [ ] No other apps using camera
- [ ] Good lighting in room
- [ ] Quiet environment

### During Interview:
- [ ] Video shows your face clearly
- [ ] Camera button toggles video on/off
- [ ] Microphone button toggles audio on/off
- [ ] Red indicator shows when muted/off
- [ ] "Camera is off" overlay appears when disabled

### Controls Test:
1. **Camera Toggle:**
   - Click camera button → Video disappears
   - "Camera is off" message appears
   - Button background turns red
   - Click again → Video reappears

2. **Microphone Toggle:**
   - Click mic button → Audio muted
   - Button background turns red
   - Click again → Audio unmuted
   - Button returns to normal

---

## Browser Console Debugging

### Check for Errors:
1. Press F12 to open DevTools
2. Go to Console tab
3. Look for errors:

**Common Errors:**

```javascript
// Permission denied
NotAllowedError: Permission denied

// Camera in use
NotReadableError: Could not start video source

// No camera found
NotFoundError: Requested device not found
```

### Check Video Element:
```javascript
// In console, check if video is playing:
document.querySelector('video').paused  // Should be false
document.querySelector('video').srcObject  // Should show MediaStream
```

---

## Advanced Troubleshooting

### Check Media Stream:
```javascript
// In browser console during interview:
navigator.mediaDevices.getUserMedia({video: true, audio: true})
  .then(stream => {
    console.log('Video tracks:', stream.getVideoTracks())
    console.log('Audio tracks:', stream.getAudioTracks())
  })
  .catch(err => console.error('Error:', err))
```

### Check Available Devices:
```javascript
navigator.mediaDevices.enumerateDevices()
  .then(devices => {
    console.log('Cameras:', devices.filter(d => d.kind === 'videoinput'))
    console.log('Microphones:', devices.filter(d => d.kind === 'audioinput'))
  })
```

---

## Quick Fixes

### Fix 1: Hard Refresh
```
Windows: Ctrl + Shift + R
Mac: Cmd + Shift + R
```

### Fix 2: Clear Browser Cache
```
Chrome:
1. Settings → Privacy and security
2. Clear browsing data
3. Check "Cached images and files"
4. Clear data
```

### Fix 3: Restart Browser
1. Close all browser windows
2. Reopen browser
3. Navigate to interview page
4. Allow permissions

### Fix 4: Restart Computer
If all else fails, restart your computer to reset all media devices.

---

## Feature Improvements Made

### ✅ Video Display:
- Added explicit `.play()` call after setting srcObject
- Added video quality settings (720p)
- Added "Camera is off" overlay
- Added proper cleanup on unmount

### ✅ Camera Control:
- Implemented proper track enable/disable
- Added visual feedback (red button when off)
- Added "Camera is off" message
- Hides video element when camera off

### ✅ Microphone Control:
- Implemented proper track enable/disable
- Added visual feedback (red button when muted)
- Maintains audio track state
- Works with speech recognition

### ✅ User Experience:
- Clear visual indicators
- Smooth transitions
- Proper error handling
- Helpful error messages

---

## Still Having Issues?

### Check These:
1. ✅ Both servers running (backend + frontend)
2. ✅ Using Chrome or Edge browser
3. ✅ Camera/mic permissions granted
4. ✅ No other apps using camera
5. ✅ Browser console shows no errors

### Get Help:
1. Check browser console for errors
2. Try different browser
3. Test camera in other apps
4. Check system permissions
5. Restart everything

---

## Success Indicators

### Video Working Correctly:
- ✅ You see yourself in the video feed
- ✅ Video is smooth (not frozen)
- ✅ Camera button toggles video on/off
- ✅ "Camera is off" shows when disabled

### Audio Working Correctly:
- ✅ Microphone button toggles mute
- ✅ Red indicator when muted
- ✅ Speech recognition captures your voice
- ✅ Transcript appears when speaking

---

**If video is working, you're ready to interview! 🎉**
