const express = require('express');
const path = require('path');
const http = require('http');
const livereload = require('livereload');
const connectLivereload = require('connect-livereload');
const app = express();
const PORT = 3000;

/* NodeJS 버전 맞추기 */
/* nvm use */
/* nvm install */

/* 서버 실행시 "npm run dev" 명령어 사용 */


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

app.listen(PORT, () =>{
    console.log(`✅ http://localhost:${PORT} 에서 서버 실행 중`);
})