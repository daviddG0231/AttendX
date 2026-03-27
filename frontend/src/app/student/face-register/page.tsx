'use client'

import { useState, useRef, useCallback, useEffect } from 'react'
import { 
  Camera, CheckCircle, XCircle, ArrowRight, ArrowLeft, 
  RefreshCw, Upload, Eye, AlertTriangle, Trash2
} from 'lucide-react'

const REQUIRED_PHOTOS = 5

const POSE_INSTRUCTIONS = [
  { pose: 'Look straight at the camera', emoji: '😐', tip: 'Keep your head level and centered' },
  { pose: 'Turn slightly to the LEFT', emoji: '👈', tip: 'About 15-20 degrees' },
  { pose: 'Turn slightly to the RIGHT', emoji: '👉', tip: 'About 15-20 degrees' },
  { pose: 'Tilt your head slightly UP', emoji: '👆', tip: 'Just a small tilt' },
  { pose: 'Smile naturally', emoji: '😊', tip: 'A natural, relaxed smile' },
]

export default function FaceRegisterPage() {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [stream, setStream] = useState<MediaStream | null>(null)
  const [cameraActive, setCameraActive] = useState(false)
  const [photos, setPhotos] = useState<string[]>([])
  const [currentPose, setCurrentPose] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState<any>(null)
  const [error, setError] = useState('')
  const [mode, setMode] = useState<'choose' | 'camera' | 'upload' | 'done'>('choose')
  const [countdown, setCountdown] = useState<number | null>(null)

  // Start webcam
  const startCamera = useCallback(async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          width: { ideal: 1280 }, 
          height: { ideal: 720 },
          facingMode: 'user'
        }
      })
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
      
      setStream(mediaStream)
      setCameraActive(true)
      setMode('camera')
      setError('')
    } catch (err) {
      setError('Camera access denied. Please allow camera access and try again.')
    }
  }, [])

  // Stop webcam
  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
    setCameraActive(false)
  }, [stream])

  // Capture photo from webcam
  const capturePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return

    // Countdown effect
    setCountdown(3)
    
    const timer = setInterval(() => {
      setCountdown(prev => {
        if (prev === null || prev <= 1) {
          clearInterval(timer)
          
          // Actually capture
          const video = videoRef.current!
          const canvas = canvasRef.current!
          canvas.width = video.videoWidth
          canvas.height = video.videoHeight
          
          const ctx = canvas.getContext('2d')!
          // Mirror the image (selfie cam is mirrored)
          ctx.translate(canvas.width, 0)
          ctx.scale(-1, 1)
          ctx.drawImage(video, 0, 0)
          
          const dataUrl = canvas.toDataURL('image/jpeg', 0.9)
          
          setPhotos(prev => [...prev, dataUrl])
          setCurrentPose(prev => prev + 1)
          setCountdown(null)
          
          return null
        }
        return prev - 1
      })
    }, 800)
  }, [])

  // Remove a photo
  const removePhoto = (index: number) => {
    setPhotos(prev => prev.filter((_, i) => i !== index))
    if (currentPose > 0) setCurrentPose(prev => prev - 1)
  }

  // Handle file uploads
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files) return

    Array.from(files).forEach(file => {
      if (photos.length >= REQUIRED_PHOTOS) return
      
      const reader = new FileReader()
      reader.onloadend = () => {
        setPhotos(prev => {
          if (prev.length >= REQUIRED_PHOTOS) return prev
          return [...prev, reader.result as string]
        })
        setCurrentPose(prev => Math.min(prev + 1, REQUIRED_PHOTOS))
      }
      reader.readAsDataURL(file)
    })
  }

  // Submit photos for registration
  const submitRegistration = async () => {
    if (photos.length < REQUIRED_PHOTOS) {
      setError(`Need ${REQUIRED_PHOTOS} photos, you have ${photos.length}`)
      return
    }

    setUploading(true)
    setError('')

    try {
      // Convert data URLs to blobs for upload
      const formData = new FormData()
      
      for (let i = 0; i < photos.length; i++) {
        const response = await fetch(photos[i])
        const blob = await response.blob()
        formData.append('images', blob, `face_${i + 1}.jpg`)
      }

      // Get student ID from URL params
      const params = new URLSearchParams(window.location.search)
      const studentId = params.get('id') || 'unknown'

      const res = await fetch(
        `http://localhost:8000/api/students/${studentId}/register-face`,
        {
          method: 'POST',
          body: formData
        }
      )

      const data = await res.json()

      if (data.success) {
        setUploadResult(data)
        setMode('done')
        stopCamera()
      } else {
        setError(data.detail || 'Registration failed. Please try again with clearer photos.')
      }
    } catch (err) {
      setError('Server error. Make sure the backend is running on localhost:8000')
    } finally {
      setUploading(false)
    }
  }

  // Cleanup camera on unmount
  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
      }
    }
  }, [stream])

  // DONE screen
  if (mode === 'done') {
    return (
      <div className="min-h-screen bg-dark-950 flex items-center justify-center p-6">
        <div className="w-full max-w-md text-center">
          <div className="w-20 h-20 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-10 h-10 text-green-400" />
          </div>
          <h1 className="text-3xl font-bold mb-3">Face Registered! 🎉</h1>
          <p className="text-white/50 mb-8">
            Your face has been successfully registered. The system can now 
            recognize you automatically during lectures.
          </p>
          
          <div className="glass-card p-6 mb-8 text-left">
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-white/50">Photos processed</span>
                <span className="font-medium">{uploadResult?.images_processed || photos.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/50">Embeddings extracted</span>
                <span className="font-medium text-green-400">{uploadResult?.embeddings_extracted || photos.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/50">Status</span>
                <span className="badge-green">Active</span>
              </div>
            </div>
          </div>

          {/* Steps indicator */}
          <div className="flex items-center justify-center gap-2 mb-6">
            <div className="w-8 h-1 rounded-full bg-green-500" />
            <div className="w-8 h-1 rounded-full bg-green-500" />
            <div className="w-8 h-1 rounded-full bg-green-500" />
            <span className="text-xs text-white/30 ml-2">Complete!</span>
          </div>

          <a href="/student" className="btn-primary inline-flex items-center gap-2">
            Go to Dashboard <ArrowRight className="w-4 h-4" />
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-dark-950 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-blue-600 flex items-center justify-center mx-auto mb-4">
            <Camera className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold">Face Registration</h1>
          <p className="text-white/40 mt-2">
            We need {REQUIRED_PHOTOS} photos of your face under different poses
          </p>

          {/* Steps indicator */}
          <div className="flex items-center justify-center gap-2 mt-4">
            <div className="w-8 h-1 rounded-full bg-green-500" />
            <div className="w-8 h-1 rounded-full bg-primary-500" />
            <div className="w-8 h-1 rounded-full bg-white/10" />
            <span className="text-xs text-white/30 ml-2">Step 2 of 3</span>
          </div>
        </div>

        {error && (
          <div className="max-w-xl mx-auto mb-6 bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-400 text-sm flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            {error}
          </div>
        )}

        {/* Mode Selection */}
        {mode === 'choose' && (
          <div className="max-w-xl mx-auto grid grid-cols-2 gap-4">
            <button
              onClick={startCamera}
              className="glass-card-hover p-8 text-center"
            >
              <Camera className="w-12 h-12 text-primary-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Use Camera</h3>
              <p className="text-sm text-white/40">Take 5 photos with your webcam</p>
            </button>

            <button
              onClick={() => {
                setMode('upload')
                fileInputRef.current?.click()
              }}
              className="glass-card-hover p-8 text-center"
            >
              <Upload className="w-12 h-12 text-green-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Upload Photos</h3>
              <p className="text-sm text-white/40">Upload 5 existing photos</p>
            </button>
          </div>
        )}

        {/* Camera Mode */}
        {mode === 'camera' && (
          <div className="max-w-3xl mx-auto">
            <div className="grid lg:grid-cols-5 gap-6">
              {/* Camera Feed */}
              <div className="lg:col-span-3">
                <div className="glass-card overflow-hidden relative">
                  {/* Video */}
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full aspect-video object-cover"
                    style={{ transform: 'scaleX(-1)' }}
                  />
                  
                  {/* Countdown overlay */}
                  {countdown !== null && (
                    <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                      <span className="text-8xl font-bold text-white animate-pulse">
                        {countdown}
                      </span>
                    </div>
                  )}

                  {/* Face guide oval */}
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div className="w-48 h-64 border-2 border-dashed border-primary-400/50 rounded-full" />
                  </div>

                  {/* Pose instruction */}
                  {currentPose < REQUIRED_PHOTOS && (
                    <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/80 to-transparent p-6">
                      <div className="text-center">
                        <span className="text-3xl mb-2 block">{POSE_INSTRUCTIONS[currentPose]?.emoji}</span>
                        <p className="font-medium">{POSE_INSTRUCTIONS[currentPose]?.pose}</p>
                        <p className="text-sm text-white/50">{POSE_INSTRUCTIONS[currentPose]?.tip}</p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Capture button */}
                <div className="flex justify-center mt-4 gap-4">
                  {photos.length < REQUIRED_PHOTOS ? (
                    <button
                      onClick={capturePhoto}
                      disabled={countdown !== null}
                      className="w-16 h-16 rounded-full bg-primary-500 hover:bg-primary-600 flex items-center justify-center transition-all active:scale-90 disabled:opacity-50"
                    >
                      <Camera className="w-7 h-7 text-white" />
                    </button>
                  ) : (
                    <button
                      onClick={submitRegistration}
                      disabled={uploading}
                      className="btn-primary text-lg px-8 py-4 flex items-center gap-2"
                    >
                      {uploading ? (
                        <>
                          <RefreshCw className="w-5 h-5 animate-spin" />
                          Processing...
                        </>
                      ) : (
                        <>
                          Register Face <ArrowRight className="w-5 h-5" />
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>

              {/* Photo Grid */}
              <div className="lg:col-span-2">
                <h3 className="text-sm font-medium text-white/60 mb-3">
                  Photos ({photos.length}/{REQUIRED_PHOTOS})
                </h3>
                
                {/* Progress */}
                <div className="w-full h-2 bg-white/5 rounded-full mb-4 overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-primary-500 to-green-500 rounded-full transition-all duration-500"
                    style={{ width: `${(photos.length / REQUIRED_PHOTOS) * 100}%` }}
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  {Array.from({ length: REQUIRED_PHOTOS }).map((_, i) => (
                    <div key={i} className="aspect-square rounded-xl overflow-hidden relative">
                      {photos[i] ? (
                        <>
                          <img src={photos[i]} alt={`Photo ${i+1}`} className="w-full h-full object-cover" />
                          <div className="absolute top-1 right-1">
                            <button
                              onClick={() => removePhoto(i)}
                              className="w-6 h-6 rounded-full bg-red-500/80 flex items-center justify-center hover:bg-red-500"
                            >
                              <Trash2 className="w-3 h-3 text-white" />
                            </button>
                          </div>
                          <div className="absolute bottom-1 left-1">
                            <span className="badge-green text-[10px]">✓</span>
                          </div>
                        </>
                      ) : (
                        <div className="w-full h-full bg-white/5 border border-dashed border-white/10 flex flex-col items-center justify-center">
                          <Camera className="w-5 h-5 text-white/20 mb-1" />
                          <span className="text-[10px] text-white/20">
                            {i < POSE_INSTRUCTIONS.length ? POSE_INSTRUCTIONS[i].emoji : '📸'}
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {photos.length === REQUIRED_PHOTOS && (
                  <div className="mt-4 p-3 bg-green-500/10 border border-green-500/20 rounded-xl text-center">
                    <CheckCircle className="w-5 h-5 text-green-400 mx-auto mb-1" />
                    <p className="text-sm text-green-400">All photos captured!</p>
                    <p className="text-xs text-white/40">Click &quot;Register Face&quot; to continue</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Upload Mode */}
        {mode === 'upload' && (
          <div className="max-w-xl mx-auto">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              multiple
              onChange={handleFileUpload}
              className="hidden"
            />

            <div 
              onClick={() => fileInputRef.current?.click()}
              className="glass-card-hover p-12 text-center cursor-pointer border-2 border-dashed border-white/10 hover:border-primary-500/50"
            >
              <Upload className="w-12 h-12 text-white/30 mx-auto mb-4" />
              <p className="font-medium mb-2">Click to upload photos</p>
              <p className="text-sm text-white/40">
                Upload {REQUIRED_PHOTOS} face photos (JPG, PNG)
              </p>
            </div>

            {/* Uploaded previews */}
            {photos.length > 0 && (
              <div className="mt-6">
                <h3 className="text-sm font-medium text-white/60 mb-3">
                  Uploaded ({photos.length}/{REQUIRED_PHOTOS})
                </h3>
                <div className="grid grid-cols-5 gap-3">
                  {photos.map((photo, i) => (
                    <div key={i} className="aspect-square rounded-xl overflow-hidden relative">
                      <img src={photo} alt={`Photo ${i+1}`} className="w-full h-full object-cover" />
                      <button
                        onClick={() => removePhoto(i)}
                        className="absolute top-1 right-1 w-6 h-6 rounded-full bg-red-500/80 flex items-center justify-center"
                      >
                        <Trash2 className="w-3 h-3 text-white" />
                      </button>
                    </div>
                  ))}
                </div>

                {photos.length < REQUIRED_PHOTOS && (
                  <button 
                    onClick={() => fileInputRef.current?.click()}
                    className="btn-secondary mt-4 w-full"
                  >
                    Add more photos ({REQUIRED_PHOTOS - photos.length} remaining)
                  </button>
                )}

                {photos.length >= REQUIRED_PHOTOS && (
                  <button
                    onClick={submitRegistration}
                    disabled={uploading}
                    className="btn-primary mt-4 w-full flex items-center justify-center gap-2 py-3"
                  >
                    {uploading ? (
                      <><RefreshCw className="w-5 h-5 animate-spin" /> Processing...</>
                    ) : (
                      <>Register Face <ArrowRight className="w-5 h-5" /></>
                    )}
                  </button>
                )}
              </div>
            )}

            <button onClick={() => setMode('choose')} className="btn-secondary mt-4 w-full flex items-center justify-center gap-2">
              <ArrowLeft className="w-4 h-4" /> Back
            </button>
          </div>
        )}

        {/* Hidden canvas for capture */}
        <canvas ref={canvasRef} className="hidden" />
      </div>
    </div>
  )
}
