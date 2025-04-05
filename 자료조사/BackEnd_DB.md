<h2>PRo-AI</h2>

## AI
 GPT 모델을 호출할 수 있는 API를 운용해야 할 것 같음 .
(GPT가 죽으면 작동을 안한다는 단점) 
1. OpenAI API키 발급
2. .env파일에 API키 저장
	OPENAI_API)KEY = ####

=> GPT 자체의 API를 사용할 것 같으나 라마등 다른 것을 사용할 경우 바꿀것 염두.

ex) Ollama
<img width="634" alt="Mistral" src="https://github.com/user-attachments/assets/8eaa8340-a904-4c68-afc0-c5a89cbe6052" />


간단한 예제(Ollama)
// server.js

const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = 3000;

app.use(express.static('public'));
app.use(express.json());

app.post('/chat', async (req, res) => {
  const userMessage = req.body.message;

  try {
    const response = await axios.post('http://localhost:11434/api/generate', {
      model: 'llama2', // 또는 your-custom-model
      prompt: userMessage,
      stream: false,
    });

    res.json({ reply: response.data.response });
  } catch (err) {
    console.error(err);
    res.status(500).json({ reply: 'Error contacting Ollama' });
  }
});

app.listen(PORT, () => {
  console.log(`✅ Server running at http://localhost:${PORT}`);
});


## DB 관련
MongoDB 
1. JSON 문서에 데이터를 키-값 페어로 저장하는 Document Database


PostgreSQL
1. 객체 지향 기능 + 관계형 데이터베이스 (ORDBMS)

<img width="871" alt="스크린샷 2025-04-03 오후 6 28 26" src="https://github.com/user-attachments/assets/3218d263-8d23-473d-b7c0-471f971e1580" />


MongoDB와 달리 PostgreSQL은 미리 정의된 스키마를 사용해 저장.

미리 스키마를 정의할 필요가 없다고 판단해 MongoDB사용하고자 하나
필요할 경우 PostgreSQL이나 접근성이 쉬운 MySQL도 고려해봄 .

￼
## (주)슈퍼히어로
- 데이터는 방대함
- 하지만 정제되어 있지 않을 뿐더러 아직 어떤 형태로 되어 있는지 모름.
- 회사 외부(레퍼런스)의 잘 된 사례를 카피함
- 메인 컨셉 도출 과정
    1. 문제 정의
    2. 전하고자 하는 스토리
    3. 타겟층
    4. Client 요구사항
    5. 전달해야 하는 메시지를 만들기 위한 정보나 배경. (이렇게 만든 이유)
    6. 추가적으로 컨셉을 누르면 시나리오까지 써주면 베스트 .

-> 웹으로 해달라는 요청이 있어서 앱 패키징은 필요 없을것 같음.
(chatGPT는 외국 사례가 많으므로 한국 사례를 중심으로 교육시킬 것.)

메인 컨셉 도출 프로그램이 최종 목표

