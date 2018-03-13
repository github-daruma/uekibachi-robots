
#define encLA 2  //左A相
#define encLB 3  //左B相
#define encRA 18 //右A相
#define encRB 19 //右B相

volatile uint64_t mills, mills_old;
volatile int Ldata, Rdata, Ldt, Rdt, dt, Ldata_old, Rdata_old;
volatile int oldLA, oldLB, oldRA, oldRB;
unsigned long millis();

void setup(){
  //シリアル通信設定
  Serial.begin(230400);

  //各pinの設定
  pinMode(encLA, INPUT_PULLUP);
  pinMode(encLB, INPUT_PULLUP);
  pinMode(encRA, INPUT_PULLUP);
  pinMode(encRB, INPUT_PULLUP);
  //割り込み処理に対応させる
  attachInterrupt(digitalPinToInterrupt(encLA), count,CHANGE);
  attachInterrupt(digitalPinToInterrupt(encLB), count,CHANGE);
  attachInterrupt(digitalPinToInterrupt(encRA), count,CHANGE);
  attachInterrupt(digitalPinToInterrupt(encRB), count,CHANGE);
  //Serial.print("Start");

}

void loop(){
  mills = millis();
  dt = mills - mills_old;
  //左右のカウント数はdt[ms]間に動いた数
  Serial.print(dt);
  Serial.print(" ");
  Serial.print(Ldata - Ldata_old);
  Serial.print(" ");
  Serial.println(Rdata - Rdata_old);
  mills_old = mills;
  Ldata_old = Ldata;
  Rdata_old = Rdata;
  delay(100);
}

void count(){
  //各関数設定
  volatile int newLA, newLB, newRA, newRB, addL, addR;
  int mills;
  //各エンコーダの状態確認
  newLA = !digitalRead(encLA);
  newLB = !digitalRead(encLB);
  newRA = !digitalRead(encRA);
  newRB = !digitalRead(encRB);

  //回転判定
  if(oldLA == oldLB){
    if(oldLA != newLA) addL = -1;        //時計回り
    else if (oldLB == newLB) addL = 0;  //無回転
    else addL = 1;                      //反時計回り
  }
  else{
    if(oldLA != newLA) addL = 1;        //反時計
    else if(oldLB == newLB) addL = 0;   //無回転
    else addL = -1;                      //時計回り
  }

  if(oldRA == oldRB){
    if(oldRA != newRA) addR = -1;        //時計回り
    else if (oldRB == newRB) addR = 0;  //無回転
    else addR = 1;                      //反時計
  }
  else{
    if(oldRA != newRA) addR = 1;        //反時計
    else if(oldRB == newRB) addR = 0;   //無回転
    else addR = -1;                      //時計回り
  }

  //各値を更新
  oldLA = newLA;
  oldLB = newLB;
  oldRA = newRA;
  oldRB = newRB;
  //送信
  Ldata += addL;
  Rdata += addR;
  addL = 0;
  addR = 0;
}
