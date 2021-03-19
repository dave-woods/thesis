const util = require('util');
const exec = util.promisify(require('child_process').exec);

async function executePyScript(path, args) {
  try {
    const { stdout, stderr } = await exec(`python3 ${path} '${args}'`);
    return {
      stdout,
      stderr
    }
  } catch (e) {
    console.error(e)
    return {
      error: e
    }
  }
}

export default async (req, res) => {
  if (req.method === 'POST') {
    console.log('hit api')
    console.log('received', req.body.inputs)
    const strs = JSON.stringify(req.body.inputs)
    const { stdout, stderr, error } = await executePyScript('./apiscripts/test.py', strs)
    console.log('executed script')
    res.status(200).json({ stdout, stderr, error })
  }
}

