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
    counter = 0;
  }
    
  void inflate(int time) {
    counter = time;
    mode = INFLATE;
  }
  
  void deflate(int time) {
    counter = time;
    mode = DEFLATE;
  }
  
  void stop() {
    counter = 0;
  }
    
  void update() {
    
    digitalWrite(infPin, mode == INFLATE && counter > 0);
    digitalWrite(defPin, mode == DEFLATE && counter > 0);
    
    if (counter > 0) counter--;
  }
  
};

// 2 onwards 13
const int NB = 7;
Balloon balloons[NB];
const int TIME_STEP = 100;

void setup() {

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
  delay(TIME_STEP);
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
        return;
      }
      
      if (command == 'i') {
        balloons[number].inflate(time);
      }
      else if (command == 'd') {
        balloons[number].deflate(time);
      }
      else if (command == 's') {
        balloons[number].stop();
      }
    }            
  }
    
}


