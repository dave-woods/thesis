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
    console.log('received', req.body.data)
    const data = JSON.stringify(req.body.data)
    const { stdout, stderr, error } = await executePyScript('./apiscripts/newTLINKs.py', data)
    const result = {}
    if (error) {
      result['error'] = error
    } else if (stderr) {
      result['error'] = stderr
    } else {
      result['tlinks'] = JSON.parse(stdout)
    }
    console.log('executed script')
    res.status(200).json(result)
  }
}

