class Balloon {
public:
  int icounter, dcounter;  
  int counter;
  int infPin, defPin;
  typedef enum { INFLATE, DEFLATE } mode_t;
  mode_t mode;
  
  Balloon() {}
  
  Balloon(int ip, int dp) {
    infPin = ip;
    defPin = dp;
    pinMode(infPin, OUTPUT);
    pinMode(defPin, OUTPUT);
//    icounter = dcounter = 0;
    counter = 0;
  }
    
  void inflate(int time) {
//    icounter = time;
    counter = time;
    mode = INFLATE;
  }
  
  void deflate(int time) {
//    dcounter = time;
    counter = time;
    mode = DEFLATE;
  }
  
  void stop() {
//    dcounter = icounter = 0;
    counter = 0;
  }
    
  void update() {
    
//    digitalWrite(infPin, icounter > 0);
//    digitalWrite(defPin, dcounter > 0);
//    
//    if (icounter > 0) icounter--;
//    if (dcounter > 0) dcounter--;
//    
    
    digitalWrite(infPin, mode == INFLATE && counter > 0);
    digitalWrite(defPin, mode == DEFLATE && counter > 0);
    
    if (counter > 0) counter--;
  }
  
};

// 2 onwards 13
const int NB = 7;
Balloon balloons[NB];


void setup() {
  // initialize serial:
  Serial.begin(9600);
  
  // 2 - 11
  for (int i = 1; i <= 5; i++) {
    balloons[i-1] = Balloon(i*2, i*2+1);
  }
  
  balloons[5] = Balloon(12, A0);
  balloons[6] = Balloon(A1, A2);

}

void loop() {
  for (int i = 0; i < NB; i++) {
    balloons[i].update();
  }
  delay(1000);
}

void serialEvent() {
  
  while (Serial.available() >= 5) {
    char buf[6];
    Serial.readBytes(buf, 5);
    if (buf[0] == '?' && buf[4] == '!') {
      char command = buf[1];
      unsigned char number = (unsigned char) buf[2];
      unsigned char time = (unsigned char) buf[3];
      
      if (number > NB) {
        Serial.println("over NB");
        return;
      }
      
      if (command == 'i') {
        balloons[number].inflate(time);
//        Serial.println("inflating...");
      }
      else if (command == 'd') {
        balloons[number].deflate(time);
//        Serial.println("deflating...");
      }
      else if (command == 's') {
        balloons[number].stop();
      }
    }            
    else {
//      Serial.println("invalid message header and footer");
    }  
  }
  
//  else if (Serial.available() > 5) {
//    while (Serial.available()) {
//      Serial.read();
//    }
//  }
    
}


