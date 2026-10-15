(function () {
  var head = document.querySelector('.site-head');
  var btn = document.getElementById('menu-btn');
  function setMenu(open) {
    if (!head) return;
    head.classList.toggle('open', open);
    document.body.classList.toggle('menu-open', open);
    if (btn) { btn.setAttribute('aria-expanded', open ? 'true' : 'false'); btn.textContent = open ? '닫기' : '메뉴'; }
  }
  if (btn) btn.addEventListener('click', function () { setMenu(!head.classList.contains('open')); });

  // 하단 탭바
  document.querySelectorAll('.tabbar [data-open]').forEach(function (b) {
    b.addEventListener('click', function () {
      var mode = b.getAttribute('data-open');
      var isOpen = head.classList.contains('open');
      if (mode === 'menu') { setMenu(!isOpen); window.scrollTo(0, window.scrollY); return; }
      var home = document.getElementById('q');
      if (home && home.getBoundingClientRect) { setMenu(false); home.scrollIntoView({ block: 'center' }); home.focus(); return; }
      setMenu(true);
      var mq = document.getElementById('mq'); if (mq) mq.focus();
    });
  });
  var top = document.querySelector('.tabbar [data-top]');
  if (top) top.addEventListener('click', function (e) { e.preventDefault(); setMenu(false); window.scrollTo({ top: 0, behavior: 'smooth' }); });

  // 메뉴 안의 링크를 누르면 메뉴 닫기
  document.querySelectorAll('.mnav a').forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });

  // 넓은 표: 옆으로 밀어 보기 안내
  function markTables() {
    document.querySelectorAll('.tbl').forEach(function (w) {
      var over = w.scrollWidth > w.clientWidth + 4;
      var prev = w.previousElementSibling;
      var has = prev && prev.classList && prev.classList.contains('swipe');
      if (over && !has) { var d = document.createElement('div'); d.className = 'swipe'; d.textContent = '표를 옆으로 밀어서 보세요 →'; w.parentNode.insertBefore(d, w); }
      if (!over && has) { prev.remove(); }
    });
  }
  markTables();
  window.addEventListener('resize', markTables);

  // 복사 버튼
  function copyText(text, done) {
    function fallback() {
      var ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select();
      var ok = false; try { ok = document.execCommand('copy'); } catch (e) {} ta.remove(); done(ok);
    }
    try { navigator.clipboard.writeText(text).then(function () { done(true); }, fallback); } catch (e) { fallback(); }
  }
  document.querySelectorAll('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      copyText(b.getAttribute('data-copy'), function (ok) { var o = b.textContent; b.textContent = ok ? '복사됨' : '길게 눌러 복사'; setTimeout(function () { b.textContent = o; }, 1600); });
    });
  });
  function copyMsg(ok, el) {
    var m = document.getElementById('copy-msg');
    if (m) m.textContent = ok ? '복사했습니다. 카카오톡 대화창에 붙여넣어 보내 주세요.' : '복사가 안 되면 위 내용을 길게 눌러 직접 복사해 주세요.';
    if (!ok && el) { el.focus(); el.select(); }
  }
  document.querySelectorAll('[data-copy-from]').forEach(function (b) {
    b.addEventListener('click', function () {
      var el = document.getElementById(b.getAttribute('data-copy-from'));
      copyText(el.value, function (ok) { copyMsg(ok, el); });
    });
  });

  // 상담 신청서
  var form = document.getElementById('consult');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var err = document.getElementById('f-error');
      var name = form.elements.name.value.trim(), phone = form.elements.phone.value.trim();
      var msg = '';
      if (!name) msg = '이름을 입력해 주세요.';
      else if (phone.replace(/[^0-9]/g, '').length < 9) msg = '연락처를 숫자로 입력해 주세요. 예: 010-1234-5678';
      else if (!document.getElementById('f-agree').checked) msg = '개인정보 수집·이용에 동의해 주세요.';
      if (msg) { err.textContent = msg; err.hidden = false; return; }
      err.hidden = true;
      var topics = Array.prototype.map.call(form.querySelectorAll('input[name=topic]:checked'), function (c) { return c.value; });
      var lines = ['[보험 상담 신청]', '이름: ' + name, '연락처: ' + phone];
      if (form.elements.age.value) lines.push('나이대: ' + form.elements.age.value);
      if (topics.length) lines.push('관심 분야: ' + topics.join(', '));
      lines.push('연락 시간: ' + (form.elements.time.value || '상관없음'));
      if (form.elements.msg.value.trim()) lines.push('문의 내용: ' + form.elements.msg.value.trim());
      document.getElementById('done-text').value = lines.join(String.fromCharCode(10));
      document.getElementById('done').hidden = false;
      form.hidden = true;
      document.getElementById('done').scrollIntoView({ block: 'start' });
    });
    var send = document.getElementById('send-kakao');
    if (send) send.addEventListener('click', function () {
      var el = document.getElementById('done-text');
      copyText(el.value, function (ok) { copyMsg(ok, el); });
    });
  }

  // 검색(홈·메뉴 공용)
  var IDX = [{"k": "ch01", "t": "보험증권 읽는 법과 보장분석", "n": "CHAPTER 01", "g": "보험 기초", "s": "보험증권은 계약의 '설계도'입니다. 다섯 가지 항목만 읽을 줄 알아도 내 보험의 80%를 이해할 수 있습니다. 보험증권이란 무엇인가 보험증권에서 반드시 확인할 5가지 보장분석이 필요한 네 가지 신호 보험 리모델링 시 주의할 점"}, {"k": "ch02", "t": "갱신형 vs 비갱신형, 무엇이 유리할까", "n": "CHAPTER 02", "g": "보험 기초", "s": "\"처음엔 싸다\"와 \"끝까지 같다\"의 차이. 갱신 구조를 이해하지 못하면 노후에 보험을 지킬 수 없습니다. 두 방식의 기본 구조 보험료 흐름 비교 — 그림으로 보기 그렇다면 갱신형은 무조건 나쁜가? 현명한 조합 전략"}, {"k": "ch03", "t": "계약 전 알릴의무 — 표준체·간편체·간편실손", "n": "CHAPTER 03", "g": "보험 기초", "s": "보험금 분쟁의 상당수는 '가입할 때 알리지 않은 병력'에서 시작됩니다. 질문의 기간과 용어를 정확히 이해하는 것이 최선의 예방책입니다. 알릴의무란 표준체(일반심사) 알릴의무 질문 간편체(유병자) 알릴의무 — '3·N·5' 구조 간편실손 알릴의무 헷갈리는 용어 정확히 알기 알릴 사항이 있을 때의 선택지"}, {"k": "ch04", "t": "사망의 범주와 사망보험금", "n": "CHAPTER 04", "g": "사망·장해", "s": "같은 '사망'이라도 보험에서는 원인에 따라 네 가지로 나뉩니다. 내 사망보장이 어느 범주까지 덮는지부터 확인하세요. 보험이 사망을 나누는 방식 생명보험사 vs 손해보험사 사망보장 비교 연령대별 사망자 수로 본 위험의 크기 경제적 가장이 부재하면 얼마가 필요할까 종신보험의 다섯 가지 활용법"}, {"k": "ch05", "t": "통계로 보는 사망 위험 — 한국인은 무엇으로 사망하는가", "n": "CHAPTER 05", "g": "사망·장해", "s": "보험 설계는 '막연한 불안'이 아니라 '확률'에 근거해야 합니다. 사망원인 통계는 어떤 보장을 먼저 준비해야 하는지 알려 주는 가장 객관적인 지도입니다. 2023년 사망원인 순위 TOP 10 40년 추이가 말해 주는 것 성별로 다른 사망원인 통계를 보장으로 바꾸는 법"}, {"k": "ch06", "t": "상해·질병 후유장해와 지급률", "n": "CHAPTER 06", "g": "사망·장해", "s": "장애는 대부분 '태어날 때'가 아니라 '살면서' 생깁니다. 후유장해 보장은 사망보다 확률이 높고, 가계에 남기는 부담은 더 오래갑니다. 장해의 88.1%는 후천적 원인 후유장해 보험금의 기본 원리 신체 부위별 장해지급률 한눈에 보기 뇌졸중 후유장해는 어떻게 평가할까 — ADLs 합산평가 상해후유장해 vs 질병후유장해"}, {"k": "ch07", "t": "CI보험 vs GI보험", "n": "CHAPTER 07", "g": "암·뇌·심장", "s": "'중대한'이라는 세 글자가 보험금 지급의 문턱을 얼마나 높이는지 아는 것이 CI보험 이해의 시작입니다. 두 보험의 정의 CI보험의 보험금 지급 사유 '중대한'의 함정 — CI보험 분쟁이 많은 이유 CI·GI보험과 일반 건강보험 비교"}, {"k": "ch08", "t": "암의 발생 원인과 통계", "n": "CHAPTER 08", "g": "암·뇌·심장", "s": "한 해 28만 명이 새로 암 진단을 받습니다. 암이 왜 생기는지, 어떤 암이 많은지 알면 어떤 보장이 필요한지가 보입니다. 암은 왜 생기는가 — 세 가지 원인 암의 세 가지 특성과 보험 한국인의 암 발생 현황 수도권 대형병원 쏠림과 치료비 암 진단비, 얼마나 준비할까"}, {"k": "ch09", "t": "암의 검사·진단과 병기(TNM)", "n": "CHAPTER 09", "g": "암·뇌·심장", "s": "암 진단비는 '언제' 지급될까요? 그리고 '몇 기'인지가 보험에서 왜 중요할까요? 검사부터 병기 분류까지 차례로 살펴봅니다. 암을 찾아내는 네 가지 검사 병기의 기본 — 제자리암부터 4기까지 TNM 분류 — 암의 진행 정도를 나타내는 국제 표준 요약병기별 비율 — 원격전이는 약 20% 보험금 청구 시 필요한 서류"}, {"k": "ch10", "t": "암 치료의 진화와 암보험 트렌드", "n": "CHAPTER 10", "g": "암·뇌·심장", "s": "암 치료는 '자르고, 태우고, 독으로 죽이는' 시대에서 '표적을 겨냥하고 면역을 깨우는' 시대로 바뀌었습니다. 암보험도 그 변화를 따라 다섯 세대를 거쳐 왔습니다. 암보험의 5세대 변천 암 주요 치료 ① 수술 암 주요 치료 ② 항암약물치료 암 주요 치료 ③ 항암방사선치료 치료 담보를 고를 때 확인할 다섯 가지"}, {"k": "ch11", "t": "수술의 분류 — 종수술 표 읽는 법", "n": "CHAPTER 11", "g": "암·뇌·심장", "s": "'1~5종 수술비'는 같은 수술이라도 어디를, 어떤 방식으로 하느냐에 따라 등급이 달라집니다. 수술분류표의 원리를 이해하면 받을 보험금을 미리 계산할 수 있습니다. 약관에서 말하는 '수술'이란 ① 일반적인 질병·재해(상해) 치료 목적의 수술 ② 악성신생물(암)의 치료 목적 수술 ③ 악성신생물 근치·두개내 신생물 근치 방사선 조사 60일 규칙 — 반복 수술은 어떻게 계산할까"}, {"k": "ch12", "t": "산정특례 제도", "n": "CHAPTER 12", "g": "암·뇌·심장", "s": "암 환자의 병원비가 생각보다 적게 나오는 이유, 바로 산정특례 덕분입니다. 그리고 이제는 민간보험도 산정특례를 기준으로 보험금을 지급합니다. 산정특례란 질병별 산정특례 본인부담률과 적용기간 산정특례가 바꾼 민간보험 — '산정특례 진단비' 산정특례와 민간보험은 중복 혜택"}, {"k": "ch13", "t": "뇌혈관질환 — 진단·치료와 보장 범위", "n": "CHAPTER 13", "g": "암·뇌·심장", "s": "뇌출혈 진단비만 있다면 뇌혈관질환 환자 100명 중 8명만 보장받습니다. 담보 이름에 숨은 '보장 범위'를 확인해야 하는 이유입니다. 뇌·심장 보장이 중요한 이유 뇌·심 진단 방법 뇌·심 치료 방법 뇌혈관질환의 보장 범위 — 동심원으로 이해하기 뇌 보장, 이렇게 설계하세요"}, {"k": "ch14", "t": "심장질환 — 보장 범위와 상병코드", "n": "CHAPTER 14", "g": "암·뇌·심장", "s": "급성심근경색 진단비가 보장하는 범위는 심장질환 전체의 약 6%입니다. 나머지 94%는 어떻게 대비할까요? 심장질환의 보장 범위 산정특례 심장질환 상병명 심장 순환계질환 분류(I00~I52) 심장 담보 단계별 이해"}, {"k": "ch15", "t": "수술 트렌드의 변화와 수술비 담보의 종류", "n": "CHAPTER 15", "g": "암·뇌·심장", "s": "배를 열던 수술에서 칼을 대지 않는 시술로. 수술이 작아질수록 '어떤 수술비 담보를 가졌는가'가 보험금을 좌우합니다. 수술의 네 세대 수술비 담보 4종류 비교 담보별 자세히 보기 같은 시술, 담보마다 다른 결과 어디서 수술을 많이 받을까 — 요양기관 종별 점유율"}, {"k": "ch16", "t": "통계로 보는 주요 수술 — 건수·진료비·입원일수", "n": "CHAPTER 16", "g": "암·뇌·심장", "s": "가장 많이 받는 수술, 가장 비싼 수술, 가장 오래 입원하는 수술. 숫자로 보면 내게 필요한 수술 보장이 보입니다. 가장 많이 받는 수술 TOP 7 가장 많은 진료비가 드는 수술 TOP 7 수술 1건당 진료비 — 가장 비싼 수술 수술 1건당 입원일수 — 가장 오래 입원하는 수술 통계를 보장으로 바꾸기"}, {"k": "ch17", "t": "공적 장기요양보험과 노인성 질환", "n": "CHAPTER 17", "g": "간병·치매", "s": "치매나 뇌졸중으로 혼자 생활하기 어려워졌을 때 국가가 돌봄 비용의 대부분을 지원하는 제도, 노인장기요양보험을 알아봅니다. 노인장기요양보험이란 노인성 질환의 범위 장기요양급여의 종류 신청부터 이용까지"}, {"k": "ch18", "t": "장기요양 등급과 비용, 치매 척도(CDR)", "n": "CHAPTER 18", "g": "간병·치매", "s": "몇 등급을 받느냐에 따라 한 달에 쓸 수 있는 금액이 두 배 가까이 차이 납니다. 민간 간병·치매보험의 보험금도 이 등급과 CDR 점수를 기준으로 지급됩니다. 장기요양 등급별 기준 CDR(임상치매척도) — 치매보험의 기준 재가급여 비용(2025년 기준) 시설급여 비용(2025년 기준)"}, {"k": "ch19", "t": "장기요양 이용 현황, 요양병원과 요양원, 간병보험", "n": "CHAPTER 19", "g": "간병·치매", "s": "요양병원과 요양원은 이름은 비슷하지만 법, 대상, 비용, 적용 보험이 모두 다릅니다. 간병보험도 '사람을 보내 주는' 방식과 '돈을 주는' 방식으로 나뉩니다. 장기요양 급여 종류별 이용 현황 요양병원과 요양원의 차이 간병보험의 두 가지 방식"}, {"k": "ch20", "t": "종신보험으로 준비하는 노후 — 종류, 연금전환, 사망보험금 유동화", "n": "CHAPTER 20", "g": "종신·연금", "s": "종신보험은 '죽어야 받는 보험'이라는 인식이 강합니다. 하지만 설계와 활용에 따라 노후 소득과 상속 재원을 동시에 준비하는 도구가 될 수 있습니다. 노후 준비에서 종신보험의 역할 종신보험의 종류 연금전환 — 사망보장을 노후 소득으로 사망보험금 유동화 — 살아 있을 때 미리 받기 보험료가 부담될 때의 선택지 '단기납 종신'과 환급률 마케팅 주의"}, {"k": "ch21", "t": "노후자금과 연금 3층 보장", "n": "CHAPTER 21", "g": "종신·연금", "s": "평균수명은 늘었는데 은퇴 시점은 그대로입니다. 국민연금·퇴직연금·개인연금의 3층 구조로 소득 공백을 메우는 법을 알아봅니다. 경험생명표로 본 수명 연장 연금 3층 보장체계 노후 필요자금 계산해 보기"}, {"k": "ch22", "t": "세제적격 연금 — 연금저축과 IRP 세액공제", "n": "CHAPTER 22", "g": "종신·연금", "s": "연말정산에서 최대 148만 5천 원을 돌려받는 방법. 단, 중도에 깨면 그 혜택을 토해 내야 합니다. 가입 대상과 세액공제율 납입액별 세금 절감 효과 가입 시 유의사항 연금저축보험 vs 연금저축펀드 vs IRP 세제비적격 연금보험과 비교"}, {"k": "ch23", "t": "상속재원 마련 — 수익자 지정, 상속세, 증여 활용", "n": "CHAPTER 23", "g": "종신·연금", "s": "사망보험금은 '누가 받는지'를 정하지 않으면 법이 정해 줍니다. 그리고 그 결과는 가족 간 분쟁과 세금으로 이어질 수 있습니다. 민법이 정한 상속 순위 수익자 지정이 필요한 이유 상속세 기본 구조 보험으로 상속세를 준비하는 법 상속세 계산 실전 예시 사전 증여와 증여재산공제 상속재원 설계 4단계"}, {"k": "ch24", "t": "변액보험 — 구조, 최저보증, 비용과 주의점", "n": "CHAPTER 24", "g": "종신·연금", "s": "변액보험은 '보험'과 '펀드'를 합친 상품입니다. 오래 유지하면 물가를 이기는 수익을 기대할 수 있지만, 구조를 모르고 가입하면 원금 손실과 높은 비용에 실망하기 쉽습니다. 변액보험이란 변액보험의 종류 최저보증 옵션 이해하기 비용 구조 — 왜 초기에 원금 손실이 클까 펀드 관리 — 가입보다 중요한 '유지 중 관리' 변액연금 vs 연금저축펀드 vs 일반 연금보험 가입 전 확인할 것 — 적합성 진단과 청약철회"}, {"k": "ch25", "t": "자동차보험의 주요 담보와 부상등급", "n": "CHAPTER 25", "g": "자동차보험", "s": "자동차보험은 의무보험과 임의보험으로 구성됩니다. 담보 하나하나가 누구의, 어떤 손해를 보상하는지 정확히 알아야 사고 후 당황하지 않습니다. 자동차보험의 주요 담보 대인배상 I(책임보험)의 보상 한도 자동차사고 부상등급(1~14급)"}, {"k": "ch26", "t": "운전자보험 — 사고 후 세 가지 책임과 12대 중과실", "n": "CHAPTER 26", "g": "자동차보험", "s": "자동차보험에 가입했으니 사고가 나도 괜찮다? 형사처벌은 자동차보험이 대신 받아 주지 않습니다. 교통사고 발생 시 지는 세 가지 책임 자동차보험 영역 vs 운전자보험 영역 형사처벌 대상 사고 — 12대 중과실 운전자보험 핵심 담보 정리"}, {"k": "ch27", "t": "운전자보험 변천사 — 2009년부터 2024년까지", "n": "CHAPTER 27", "g": "자동차보험", "s": "운전자보험의 비용 담보는 법 개정과 함께 바뀌어 왔습니다. 오래전에 가입한 운전자보험이라면 지금의 형사 절차를 감당하지 못할 수 있습니다. 연도별 주요 변화 변화의 배경 이해하기"}, {"k": "ch28", "t": "2026년의 변화 — 경찰조사 단계와 변호사 현물급부", "n": "CHAPTER 28", "g": "자동차보험", "s": "교통사고 대응의 무게중심이 '재판'에서 '첫 경찰 조사'로 옮겨 가고 있습니다. 운전자보험은 변호사 비용을 주는 방식에서 변호사를 직접 붙여 주는 방식으로 진화하고 있습니다. 2026년 10월, 달라지는 형사 구조 변호사 '현물급부'란 보험사별 변호사 현물급부 비교(2026년) 내 운전자보험, 지금 점검할 것"}, {"k": "ch29", "t": "치아보험 — 급여·비급여 구조와 가입 전 주의사항", "n": "CHAPTER 29", "g": "치아·화재", "s": "치과 치료비의 대부분은 비급여이고, 실손보험은 치과 비급여를 보상하지 않습니다. 치아보험이 따로 존재하는 이유입니다. 치과 치료비의 급여·비급여 구분 치아보험의 주요 담보 치아보험 계약 전 알릴의무 가입 전 주의사항 5가지"}, {"k": "ch30", "t": "치과 치료의 종류와 비용", "n": "CHAPTER 30", "g": "치아·화재", "s": "치과에서 듣는 낯선 용어들, 그리고 영수증의 금액이 왜 그렇게 나오는지 한 번에 정리합니다. 잇몸 치료 — 치주질환의 진행 단계 보존치료 — 자연치아를 살리는 치료 보철치료 — 잃은 치아를 대신하는 치료 보존치료 재료별 특징 치아보험 청구 시 확인할 것"}, {"k": "ch31", "t": "주택화재보험과 실화책임법", "n": "CHAPTER 31", "g": "치아·화재", "s": "\"작은 실수로 낸 불이니까 괜찮겠지\"는 2009년 이전 이야기입니다. 지금은 실수로 낸 불이 이웃집에 번지면 그 손해를 모두 배상해야 합니다. 실화책임에 관한 법률(2009.5.8 시행) 임차인 과실 화재 시 보험금의 흐름 주택화재보험의 주요 담보 가입금액 정하기 — 비례보상에 주의"}, {"k": "ch32", "t": "의료실비 변천사 — 1세대부터 4세대까지", "n": "CHAPTER 32", "g": "실손보험", "s": "같은 '실손'이라도 2008년에 가입한 사람과 2022년에 가입한 사람의 보장은 전혀 다릅니다. 내 실손이 몇 세대인지부터 확인하세요. 세대 구분 한눈에 보기 세대별 그 밖의 차이 실손 제도 변화의 주요 연표"}, {"k": "ch33", "t": "실손에서 보상하지 않는 사항", "n": "CHAPTER 33", "g": "실손보험", "s": "실손은 '병원비면 다 된다'는 보험이 아닙니다. 약관이 열거한 보상하지 않는 손해를 알아야 청구 거절에 당황하지 않습니다. 질병코드로 정한 보상 제외 항목 그 밖에 보상하지 않는 사항 자주 거절되는 청구 사례와 대응"}, {"k": "ch34", "t": "4세대 실손의 주요 특징 — 일반·유병자·노후", "n": "CHAPTER 34", "g": "실손보험", "s": "4세대 실손은 하나가 아닙니다. 일반 실손, 유병자 실손, 노후 실손은 구조와 자기부담이 다릅니다. 4세대 실손의료보험(일반) 4세대 유병자 실손의료보험 4세대 노후 실손의료보험 세 상품 비교 요약"}, {"k": "ch35", "t": "보험료 차등제와 구실손 vs 4세대 유불리", "n": "CHAPTER 35", "g": "실손보험", "s": "4세대 실손은 비급여를 많이 쓰면 다음 해 보험료가 최대 4배가 됩니다. 구실손을 지킬지, 4세대로 갈아탈지 판단하는 기준을 정리합니다. 실손보험 보험료 차등제 구실손 vs 4세대 실손 — 유불리 비교 누구에게 무엇이 유리할까"}, {"k": "ch36", "t": "5세대 실손보험, 무엇이 달라지나", "n": "CHAPTER 36", "g": "실손보험", "s": "\"두 마리 토끼는 못 잡는다.\" 5세대 실손은 보험료를 크게 낮추는 대신, 병원비를 돌려받는 조건을 까다롭게 만들었습니다. 5세대 실손의 세 가지 핵심 변화 '중증'과 '비중증' 비급여의 구분 40세 남성 기준 보험료 비교 실제 의료비 지출과 실손보험 효용"}, {"k": "ch37", "t": "5세대 전환 손익 계산 — BEP로 판단하기", "n": "CHAPTER 37", "g": "실손보험", "s": "BEP(손익분기점)란 '1세대를 유지해 더 내는 보험료'와 '1세대가 더 돌려주는 의료비'가 같아지는 의료비 지출 수준입니다. 이 숫자를 넘게 쓸 사람이면 1세대 유지, 아니면 전환이 유리합니다. BEP 계산의 원리 시나리오 ① 기본 시나리오(할증 없음) 시나리오 ② 5세대에서 매년 최대 할증을 받는 경우 BEP 계산 워크시트 — 내 숫자로 해 보기"}, {"k": "ch38", "t": "5세대 전환 평가 주요 포인트", "n": "CHAPTER 38", "g": "실손보험", "s": "계산이 끝났다면 마지막으로 세 가지를 점검합니다. 보험료를 끝까지 낼 수 있는가, 통원 치료 한도는 충분한가, 1세대 보험료는 앞으로 얼마나 오를까. 포인트 ① 보험료 납입 여력 포인트 ② 비급여 통원 치료의 한도와 횟수 포인트 ③ 1세대 인상률의 미래 전환 의사결정 흐름도 전환 후 보완 전략"}, {"k": "ch39", "t": "본인부담상한제와 재난적 의료비 지원", "n": "CHAPTER 39", "g": "정부지원", "s": "한 해 병원비가 일정 금액을 넘으면 국가가 돌려줍니다. 그런데 신청하지 않으면 3년 뒤 사라집니다. ① 본인부담상한제 ② 재난적 의료비 지원 사업"}, {"k": "ch40", "t": "산정특례·노인장기요양·임플란트와 틀니 지원", "n": "CHAPTER 40", "g": "정부지원", "s": "앞 장들에서 다룬 제도를 '정부 지원' 관점에서 다시 한 번 모았습니다. 신청 시기와 방법만 정확히 알아도 수백만 원이 달라집니다. ③ 산정특례 제도 ④ 노인장기요양보험 ⑤ 임플란트 및 틀니 지원 ⑥ 함께 알아 두면 좋은 지원"}, {"k": "ch41", "t": "보험금 청구 실전 가이드", "n": "CHAPTER 41", "g": "정부지원", "s": "보험은 청구해야 받습니다. 서류, 기한, 순서를 알면 받을 수 있는 보험금을 놓치지 않습니다. 보험금 청구의 기본 원칙 실손보험 청구 간소화 — 실손24 담보별 필요 서류 청구할 때 놓치기 쉬운 것들"}, {"k": "appA", "t": "질병분류코드(KCD) 읽는 법과 실무 분류", "n": "APPENDIX A", "g": "자료실", "s": "진단서 오른쪽 위에 적힌 알파벳과 숫자 한 줄이 보험금을 결정합니다. KCD란 보험 실무 추천 분류 11가지"}, {"k": "appB", "t": "보험 실무 질병코드 요약표", "n": "APPENDIX B", "g": "자료실", "s": "보험 청구와 가입 심사에서 자주 마주치는 코드를 분야별로 정리했습니다. 전체 목록은 통계청 KCD를 참고하세요. 1. 암·종양(C / D 코드) 2. 뇌·심장·혈관(I / G 코드) 3. 척추·관절·근골격(M 코드) 4. 소화기·간(K 코드) 5. 호흡기(J 코드) 6. 내분비·대사(E 코드) 7. 정신·신경(F / G 코드) 8. 상해·골절·사고(S / T / V / W / X / Y 코드) 9. 눈·귀(H 코드) 10. 감염(A / B / U 코드) 11. 피부·증상·검진(L / R / Z 코드) 12. 출생기·선천기형(P / Q 코드)"}, {"k": "appC", "t": "보험 용어 사전", "n": "APPENDIX C", "g": "자료실", "s": "이 책에 나온 주요 용어를 가나다순으로 정리했습니다."}, {"k": "appD", "t": "우리 가족 보장분석 워크시트", "n": "APPENDIX D", "g": "자료실", "s": "이 페이지를 인쇄해 가족별로 채워 보세요. 같은 위험이라도 담보 정의가 다르면 따로 적습니다. ① 보유 계약 목록 ② 위험별 보장 금액(만 원) ③ 판단과 실행 계획"}];
  function norm(s) { return (s || '').toLowerCase().replace(/\s+/g, ''); }
  document.querySelectorAll('[data-search]').forEach(function (q) {
    var box = q.parentNode.querySelector('.results');
    if (!box) return;
    function render() {
      var v = norm(q.value);
      if (!v) { box.hidden = true; box.innerHTML = ''; return; }
      var hits = IDX.map(function (it) {
        var score = 0;
        if (norm(it.t).indexOf(v) >= 0) score += 3;
        if (norm(it.g).indexOf(v) >= 0) score += 2;
        if (norm(it.s).indexOf(v) >= 0) score += 1;
        return { it: it, score: score };
      }).filter(function (h) { return h.score > 0; })
        .sort(function (a, b) { return b.score - a.score; }).slice(0, 8);
      box.innerHTML = hits.length ? hits.map(function (h) {
        return '<a href="' + h.it.k + '.html">' + h.it.t + '<small>' + h.it.g + ' · ' + h.it.n + '</small></a>';
      }).join('') : '<div class="none">찾는 주제가 없습니다. 다른 단어로 검색해 보세요.</div>';
      box.hidden = false;
    }
    q.addEventListener('input', render);
    q.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { var a = box.querySelector('a'); if (a) { window.location.href = a.getAttribute('href'); } }
      if (e.key === 'Escape') { q.value = ''; render(); }
    });
    document.addEventListener('click', function (e) { if (!box.contains(e.target) && e.target !== q) { box.hidden = true; } });
  });
})();
