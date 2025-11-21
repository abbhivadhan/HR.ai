# 🔍 Video Debug Steps

## Quick Debugging

### Step 1: Open Browser Console
Press `F12` or right-click → Inspect → Console tab

### Step 2: Start Interview
Click "Start Interview" and watch the console

### Step 3: Look for These Messages

#### ✅ Success Messages:
```
Requesting camera and microphone access...
Media stream obtained: MediaStream {...}
Video tracks: [MediaStreamTrack {...}]
Audio tracks: [MediaStreamTrack {...}]
Setting video srcObject...
Video playing successfully!
```

#### ❌ Error Messages:
```
Error accessing media devices: NotAllowedError
Error playing video: ...
Video ref is null!
```

---

## What Changed

### 1. **Better Timing**
- Set states FIRST (cameraEnabled, micEnabled, interviewState)
- THEN set up video with 100ms delay
- This ensures DOM is ready before accessing video element

### 2. **Improved Rendering**
- Changed video container to solid black background
- Added `min-h-[400px]` to ensure container has height
- Used inline styles for video element
- Changed from className to style.display for better control

### 3. **Enhanced Debugging**
- Added console.log statements throughout
- Shows stream info, tracks, and video element status
- Helps identify exactly where the issue occurs

### 4. **Better Video Setup**
- Added `onloadedmetadata` handler
- Tries to play immediately AND after metadata loads
- Logs success/failure at each step

---

## Manual Test in Console

### Test 1: Check if camera works
```javascript
navigator.mediaDevices.getUserMedia({video: true, audio: true})
  .then(stream => {
    console.log('✅ Camera works!', stream)
    console.log('Video tracks:', stream.getVideoTracks())
    stream.getTracks().forEach(track => track.stop())
  })
  .catch(err => console.error('❌ Camera error:', err))
```

### Test 2: Check video element
```javascript
// After starting interview, run this:
const video = document.querySelector('video')
console.log('Video element:', video)
console.log('Video srcObject:', video.srcObject)
console.log('Video paused:', video.paused)
console.log('Video readyState:', video.readyState)
```

### Test 3: Force video to play
```javascript
// If video exists but not playing:
const video = document.querySelector('video')
if (video && video.srcObject) {
  video.play()
    .then(() => console.log('✅ Video now playing!'))
    .catch(err => console.error('❌ Cannot play:', err))
}
```

---

## Common Issues & Fixes

### Issue: "Video ref is null!"
**Cause:** Video element not rendered yet
**Fix:** Already fixed with 100ms delay

### Issue: Video element exists but black screen
**Cause:** srcObject not set or stream not active
**Fix:** Check console for stream info

### Issue: "NotAllowedError"
**Cause:** Permissions denied
**Fix:** 
1. Click 🔒 in address bar
2. Allow camera and microphone
3. Refresh page

### Issue: Video shows briefly then disappears
**Cause:** cameraEnabled state changing
**Fix:** Check toggle functions aren't being called automatically

---

## Expected Console Output

### When Everything Works:
```
Requesting camera and microphone access...
Media stream obtained: MediaStream {id: "...", active: true}
Video tracks: [MediaStreamTrack {kind: "video", enabled: true, ...}]
Audio tracks: [MediaStreamTrack {kind: "audio", enabled: true, ...}]
Setting video srcObject...
Setting up video stream... [MediaStreamTrack {...}]
Video metadata loaded, attempting to play...
Video playing successfully!
Video started immediately
```

### When There's a Problem:
```
Requesting camera and microphone access...
Error accessing media devices: NotAllowedError: Permission denied
```

OR

```
Setting video srcObject...
Video ref is null!
```

---

## Quick Fixes to Try

### Fix 1: Hard Refresh
```
Windows: Ctrl + Shift + R
Mac: Cmd + Shift + R
```

### Fix 2: Clear Site Data
```
1. F12 → Application tab
2. Clear storage → Clear site data
3. Refresh page
```

### Fix 3: Try Different Browser
- Chrome (best)
- Edge (best)
- Firefox (may have issues)

### Fix 4: Check Video Element Directly
```javascript
// In console after starting interview:
const video = document.querySelector('video')
console.log('Video display:', window.getComputedStyle(video).display)
console.log('Video visibility:', window.getComputedStyle(video).visibility)
console.log('Video width:', video.offsetWidth)
console.log('Video height:', video.offsetHeight)
```

---

## What to Report

If video still doesn't work, report:

1. **Browser & Version:**
   - Chrome 120, Edge 119, etc.

2. **Console Messages:**
   - Copy all messages from console

3. **Video Element Info:**
   ```javascript
   const video = document.querySelector('video')
   console.log({
     exists: !!video,
     srcObject: !!video?.srcObject,
     paused: video?.paused,
     display: window.getComputedStyle(video).display,
     width: video?.offsetWidth,
     height: video?.offsetHeight
   })
   ```

4. **Camera Status:**
   - Does camera light turn on?
   - Does browser show camera icon in address bar?

---

## Success Checklist

After starting interview, verify:

- [ ] Console shows "Media stream obtained"
- [ ] Console shows "Video playing successfully!"
- [ ] Camera light is on
- [ ] Browser shows camera icon in address bar
- [ ] Video element exists in DOM
- [ ] Video element has srcObject
- [ ] Video element is not paused
- [ ] Video element is visible (not display:none)
- [ ] You can see yourself in the video feed

---

## Next Steps

1. **Start interview**
2. **Open console (F12)**
3. **Check console messages**
4. **Try manual tests above**
5. **Report findings**

The debugging logs will help us identify exactly where the issue is!
