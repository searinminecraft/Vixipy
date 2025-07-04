const convert_btn = $("#start")
const progress = $("progress")
const s = $("#status small")

const { FFmpeg } = FFmpegWASM
const { downloadWithProgress, toBlobURL, fetchFile } = FFmpegUtil
const ffmpeg = new FFmpeg()

var loaded = false

const download = (blob, name) => {
    obj = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = obj
    link.download = name
    document.body.appendChild(link)
    link.click()
    link.remove()
}

const showProgress = (e) => {
    progress.removeAttr("aria-busy")
    progress.val(Math.floor((e.received / e.total) * 100))
}

const get_metadata = async (id) => {
    try {
        var resp = await fetch(`/api/illust/${id}/ugoira_meta`)
        var json = await resp.json()
    } catch {
        throw new Error("Unable to fetch Ugoira metadata")
    }

    if (json.error == true) {
        throw new Error(json.message)
    }

    return {
        zip: json.body.originalSrc.replace('https://i.pximg.net', $('#proxy').val()),
        frames: json.body.frames
    }
}

const convert = async (id, fmt) => {
    if (!loaded) return alert("Load ffmpeg.wasm first!")

    s.html("Retrieving metadata")
    progress.attr("aria-busy", "true")
    const { zip, frames } = await get_metadata(id)
    s.html("Retrieving zip file")
    const zip_f = await downloadWithProgress(zip, showProgress)
    const totalMs = frames.reduce((a, b) => (a += +b.delay, a), 0)
    const rate = frames.length / totalMs * 1000

    s.html("Preparing...")
    progress.attr("aria-busy", "true")
    const inst = new JSZip()
    const zip_o = await inst.loadAsync(zip_f)
    const blobs = {}

    await Promise.all(Object.keys(zip_o.files).map(async name => {
        const blob = await zip_o.file(name).async("blob")
        if (blob) blobs[name] = blob
    }))

    await Promise.all(frames.map(async e => {
        await ffmpeg.writeFile(e.file, await fetchFile(blobs[e.file]))
    }))

    const inputArg = `-r ${rate} -i %06d.jpg`

    const cmds = {
        mp4: `${inputArg} -c:v libx264 -pix_fmt yuv420p -vf pad=ceil(iw/2)*2:ceil(ih/2)*2 ${id}.mp4`,
        gif: `${inputArg} -filter_complex [0:v]scale=iw:-2,split[x][z];[x]palettegen[y];[z][y]paletteuse ${id}.gif`,
        apng: `${inputArg} -c:v apng -plays 0 -vsync 0 ${id}.apng`,
        webp: `${inputArg} -c:v libwebp -lossless 0 -compression_level 5 -quality 75 -loop 0 -vsync 0 ${id}.webp`,
        webm: `${inputArg} -c:v libvpx-vp9 -lossless 0 -crf 0 ${id}.webm`,
    }

    s.html("Running command...")
    const code = await ffmpeg.exec(cmds[fmt].split(/\s+/))

    if (code != 0) throw new Error(`ffmpeg exited with code ${code}`)

    const fileData = await ffmpeg.readFile(`${id}.${fmt}`)
    const final = new Blob([new Uint8Array(fileData).buffer])

    download(final, `${id}.${fmt}`)

    s.html("Done!")
    await Promise.all(frames.map(async e => {
        await ffmpeg.deleteFile(e.file)
    }))
}

const load_ffmpeg = async () => {
    if (loaded) return
    s.html("Loading ffmpeg.wasm...")
    ffmpeg.on('log', ({ message }) => {
        s.html(`ffmpeg: ${message}`)
        console.log(message)
    })

    await ffmpeg.load({
        coreURL: await toBlobURL("/static/ugoira-converter/ffmpeg-core.js", "text/javascript", true, showProgress),
        wasmURL: await toBlobURL("/ugoira-converter/ffmpeg-core.wasm", "application/wasm", true, showProgress)
    })

    s.html("")

    loaded = true
}

convert_btn.click(async () => {
    $(".controls").hide()
    $("#status").show()
    try {
        await load_ffmpeg()
        await convert($("#id").val(), $("#format").val())
    } catch (e) {
        s.html(e)
        throw e
    }
})

const vid = document.querySelector("video")
vid.addEventListener("click", ()=>{
    if (!vid.paused) {
        vid.pause()
    } else {
        vid.play()
    }
})