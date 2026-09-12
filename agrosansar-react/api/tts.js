export default async function handler(req, res) {
  try {
    const { q, tl = 'ne' } = req.query;

    if (!q) {
      return res.status(400).json({ error: 'Missing text parameter q' });
    }

    const cleanText = String(q).replace(/[•\n]/g, ' ').slice(0, 200);
    const googleTtsUrl = `https://translate.google.com/translate_tts?ie=UTF-8&q=${encodeURIComponent(cleanText)}&tl=${encodeURIComponent(tl)}&client=tw-ob`;

    // Server-side fetch without browser Referer header to prevent 404 block
    const response = await fetch(googleTtsUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      }
    });

    if (!response.ok) {
      return res.status(response.status).json({ error: 'Upstream TTS service returned ' + response.status });
    }

    const arrayBuffer = await response.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    res.setHeader('Content-Type', 'audio/mpeg');
    res.setHeader('Cache-Control', 'public, max-age=86400, s-maxage=86400');
    res.setHeader('Access-Control-Allow-Origin', '*');
    return res.status(200).send(buffer);
  } catch (err) {
    console.error('TTS API error:', err);
    return res.status(500).json({ error: err.message || 'Internal Server Error' });
  }
}
