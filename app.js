const express = require('express');
const path = require('path');
const http = require('http');
const livereload = require('livereload');
const connectLivereload = require('connect-livereload');
const { spawn } = require('child_process');
const app = express();
const PORT = 3000;
/* NodeJS 버전 맞추기 */
/* nvm use */
/* nvm install */
/* npm install express path http livereload connect-livereload */
/* 서버 실행시 "npm run dev" 명령어 사용 */

app.use(express.json());

/* 라이브 서버 관련 코드 (코드 고치고 저장하면 알아서 새로고침) */
const liveReloadServer = livereload.createServer();
liveReloadServer.watch(path.join(__dirname, 'public'))
app.use(connectLivereload())
liveReloadServer.server.once('connection', () =>{
    setTimeout(() => {
        liveReloadServer.refresh("/");
    }, 100);
})
/* ---------------------------------------------- */

app.use(express.static('public'));

app.get('/', (req, res) => {
    res.redirect('/html/index.html')
});

app.post("/chatAI", (req, res) => {
    const problem = req.body.problem || "";
    const inputData = { problem };
    const pythonScriptPath = path.join(__dirname, "LLM", "chatAI.py");
    const pyProcess = spawn("python", [pythonScriptPath,JSON.stringify(inputData)]);

    let output = "";
    let errorOutput = "";

    pyProcess.stdout.on("data", (data) => {
        output += data.toString();
    });

    pyProcess.stderr.on("data", (data) => {
        errorOutput += data.toString();
    });

    pyProcess.on("close", (code) => {
        if (code !== 0) {
            console.error("Python 오류:", errorOutput);
            return res.status(500).json({ result: "서버 오류가 발생했습니다." });
        }
        res.json({ result: output.trim() });
    });
});

app.post("/generate", (req, res) => {
    const inputData = req.body;
    console.log("받은 JSON:", inputData);
    const pythonScriptPath = path.join(__dirname, "LLM", "agent_test", "agent", "agent_test.py");
    const pyProcess = spawn("python", [pythonScriptPath, JSON.stringify(inputData)]);

    let output = "";
    let errorOutput = "";

    pyProcess.stdout.on("data", (data) => {
        output += data.toString();
    });

    pyProcess.stderr.on("data", (data) => {
        errorOutput += data.toString();
    });

    pyProcess.on("close", (code) => {
        if (code !== 0) {
            console.error("Python 오류:", errorOutput);
            return res.status(500).json({ result: "서버 오류가 발생했습니다.", error: errorOutput });
        }
        res.json({ result: output.trim() });
    });
});

app.listen(PORT, () =>{
    console.log(`✅ http://localhost:${PORT} 에서 서버 실행 중`);
})