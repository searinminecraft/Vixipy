
const pr = document.querySelector('.console')
const startbutton = document.querySelector("#start")
    const pxid = document.querySelector("#id")
    const format = document.querySelector("#format")
    const stat = document.querySelector("#status")

    const {FFmpeg} = FFmpegWASM
    const {fetchFile} = FFmpegUtil
    const ffmpeg = new FFmpeg()

    let isLoaded = false
    let inProgress = false

    function setstatus(m) {
      stat.innerHTML = m
    }

    async function getMeta(id) {
      try {
        const resp = await fetch(`/api/internal/ugoira_meta/${id}`)
        const json = await resp.json()

        return {
          zipUri: json.body.originalSrc.replace('https://i.pximg.net', '/proxy/i.pximg.net'),
          frames: json.body.frames
        }
      } catch {
        return {
          zipUri: '',
          frames: ''
        }
      }
    }

    async function getFrameBlobs(id) {
      setstatus("Step 2: Getting metadata...")
      const {zipUri, frames} = await getMeta(id)
      setstatus("Step 3: Retrieving zip file")
      const resp = await fetch(zipUri)
      const reader = await resp.body.getReader()
      const length = +(resp.headers.get("Content-Length") || 0)
      let recv = 0
      const ch = []

      while (true) {
        const {done, value} = await reader.read()
        if (done) break
        ch.push(value)
        recv += value.length
        setstatus(`Step 3: Retrieving zip file: Progress: ${recv} / ${length} bytes`)
      }

      const zb = new Blob(ch)
      const inst = new JSZip()
      const zip = await inst.loadAsync(zb)
      const blobs = {}
      await Promise.all(Object.keys(zip.files).map(async name => {
        const blob = await zip.file(name).async('blob')
        if (blob) blobs[name] = blob
      }))

      return {frames, blobs}
    }

    async function convert(id, vfr, ext) {
      inProgress = true
      const {frames, blobs} = await getFrameBlobs(id)
      const totalMs = frames.reduce((a, b) => (a += +b.delay, a), 0)
      const rate = frames.length / totalMs * 1000

      let ffconcat = 'ffconcat version 1.0\n'

      await Promise.all(frames.map(async e => {
        if (vfr) {
          ffconcat += 'file ' + e.file + '\n'
          ffconcat += 'duration ' + Number(e.delay) / 1000 + '\n'
        }
        await ffmpeg.writeFile(e.file, await fetchFile(blobs[e.file]))
      }))

      if (vfr) {
        // Fix ffmpeg concat demuxer issue. This will increase the frame count, but will fix the last frame timestamp issue.
        ffconcat += 'file ' + frames[frames.length - 1].file + '\n'
        await ffmpeg.writeFile('ffconcat.txt', ffconcat)
      }

      const inputArg = vfr ? '-f concat -i ffconcat.txt' : `-r ${rate} -i %06d.jpg`

      const cmds = {
        mp4: `${inputArg} -c:v libx264 -pix_fmt yuv420p -vf pad=ceil(iw/2)*2:ceil(ih/2)*2 ${id}.mp4`,
        gif: `${inputArg} -filter_complex [0:v]scale=iw:-2,split[x][z];[x]palettegen[y];[z][y]paletteuse ${id}.gif`,
        apng: `${inputArg} -c:v apng -plays 0 -vsync 0 ${id}.apng`,
        webp: `${inputArg} -c:v libwebp -lossless 0 -compression_level 5 -quality 75 -loop 0 -vsync 0 ${id}.webp`,
        webm: `${inputArg} -c:v libvpx-vp9 -lossless 0 -crf 0 ${id}.webm`,
      }
      setstatus("Step 4: Convert frames to specifed format...")
      const code = await ffmpeg.exec(cmds[ext].split(/\s+/))

      if (code != 0) {
        setstatus(`ERROR: ffmpeg exited with code ${code}`)
        inProgress = false
        startbutton.removeAttribute("disabled")
        return
      }

      const fileData = await ffmpeg.readFile(`${id}.${ext}`)
      setstatus("Step 5: Finalizing")

      if (['mp4', 'webm'].includes(ext)) {
        const videoBlob = new Blob([new Uint8Array(fileData).buffer], {type: `video/${ext}`})

        const link = document.createElement("a")
        link.href = obj
        link.download = `${id}.${ext}`
        document.body.appendChild(link)
        link.click()
        link.remove()
      } else {

        const imageBlob = new Blob([new Uint8Array(fileData).buffer], {type: `image/${ext}`})
        obj = URL.createObjectURL(imageBlob)
        const link = document.createElement("a")
        link.href = obj
        link.download = `${id}.${ext}`
        document.body.appendChild(link)
        link.click()
        link.remove()
      }

      setstatus("Step 6: clean up")

      await Promise.all(frames.map(async e => {
        await ffmpeg.deleteFile(e.file)
      }))

      setstatus("Done")
      inProgress = false
    }

    async function start() {

      if (inProgress) return
      startbutton.setAttribute("disabled", "")
      setstatus("Step 1: Load ffmpeg.wasm")
      try {
        if (!isLoaded) {
          await load()
        }
        await convert(pxid.value, true, format.value)
      } catch (e) {
        setstatus(`ERROR: ${e}`)
      }
      startbutton.removeAttribute("disabled")
    }

    const load = async () => {
      ffmpeg.on('log', ({message}) => {
        pr.scrollTo(0, pr.scrollHeight);
        pr.innerHTML += message + "\n"
        console.log(message)
      })
      await ffmpeg.load(
        {coreURL: '/static/ugoira-converter/ffmpeg-core.js'}
      )
      isLoaded = true
    }

    startbutton.addEventListener('click', () => {start()})

  
