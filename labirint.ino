#define MOTOR1_IN 2
#define MOTOR1_PWM 3
#define MOTOR2_IN 4
#define MOTOR2_PWM 5

String lastCommand = ""; // Переменная для хранения последней полученной команды
unsigned long lastCommandTime = 0; // Время получения последней команды
const unsigned long commandTimeout = 5000; // Тайм-аут 5 секунд
int value_v = 700;
String receivedCommand2; // Объявляем глобальную переменную для хранения команды


void setup() {
    Serial.begin(9600);
    pinMode(MOTOR1_IN, OUTPUT);
    pinMode(MOTOR1_PWM, OUTPUT);
    pinMode(MOTOR2_IN, OUTPUT);
    pinMode(MOTOR2_PWM, OUTPUT);
}

void loop() {
    if (Serial.available() > 0) {
        String receivedCommand = Serial.readStringUntil('|');
        Serial.println(receivedCommand);
        receivedCommand.trim(); // del probel


        // Разделение строки по символу '_'
        int delimiterIndex = receivedCommand.indexOf('_');

       
        if (delimiterIndex != -1) {
        
      // Извлечение команды из строки до символа '_'
        receivedCommand2 = receivedCommand.substring(0, delimiterIndex);
        
      // Извлечение значения из строки после символа '_'
        String valueStr = receivedCommand.substring(delimiterIndex + 1);
        
      // Преобразование строки значения в целое число
        value_v = valueStr.toInt();

                                 }

         else {
         receivedCommand2 = receivedCommand;
         value_v = 700;
          }

        lastCommand = receivedCommand2; // Обновляем последнюю полученную команду
        lastCommandTime = millis(); // Обновляем время получения последней команды
        
    }


  

    // Выполняем команду, если прошел тайм-аут или если есть новая команда
    if (lastCommand != "") {
        executeCommand(lastCommand);
        Serial.println("ok");
        lastCommand = ""; // Сбрасываем команду после выполнения
    }

    
}

void executeCommand(String command) {

        Serial.println("command:");
        Serial.println(command);
        
    if (command == "levee") {
        Serial.println("co levee");
        motorControl(400, MOTOR1_IN, MOTOR1_PWM);  // Левое колесо назад
        motorControl(-value_v, MOTOR2_IN, MOTOR2_PWM);   // Правое колесо вперед -700
        delay(60); //80
        stopMotors();
     

    } else if (command == "pravee") {
        Serial.println("co pravee");
        motorControl(800, MOTOR1_IN, MOTOR1_PWM);  //700
        motorControl(-550, MOTOR2_IN, MOTOR2_PWM);
        delay(85); //65
        stopMotors();
      //  delay(10);  // Пауза 5 секунд

    } else if (command == "pryamo") {
        Serial.println("co prymo");
        motorControl(900, MOTOR1_IN, MOTOR1_PWM);  //700
        motorControl(-600, MOTOR2_IN, MOTOR2_PWM);
        delay(90); //65 80 
        stopMotors();
       // delay(10);  // Пауза 5 секунд


      } else if (command == "pribligeniestart") {

        Serial.println("pribligenieStart");
        motorControl(700, MOTOR1_IN, MOTOR1_PWM);  // Оба колеса вперед
        motorControl(-500, MOTOR2_IN, MOTOR2_PWM);
        delay(100);
        stopMotors();
        
       

     } else if (command == "levostart") {
        
                  
        Serial.println("levostart");
        motorControl(-550, MOTOR1_IN, MOTOR1_PWM);  //povorot na levo
        motorControl(-550, MOTOR2_IN, MOTOR2_PWM);
        delay(200);
        stopMotors();
      
             
       
            
    } else if (command == "levo1") {
        Serial.println("E levo1");
       // motorControl(-300, MOTOR1_IN, MOTOR1_PWM);  // Левое колесо назад
        motorControl(-600, MOTOR2_IN, MOTOR2_PWM);   // Правое колесо вперед
        delay(65);
        stopMotors();
     
            
    } else if (command == "pravo1") {
        Serial.println("E pravo");
        motorControl(600, MOTOR1_IN, MOTOR1_PWM);  // Оба колеса назад
       // motorControl(-300, MOTOR2_IN, MOTOR2_PWM);
        delay(65);
        stopMotors();
       
  
          

      
 } else if (command == "pravoitog") {
        
        Serial.println("vp1)");
        motorControl(550, MOTOR1_IN, MOTOR1_PWM);  // Оба колеса вперед
        motorControl(-550, MOTOR2_IN, MOTOR2_PWM);
        delay(450); // 210 270 300
        stopMotors();
        delay(1000);  // Пауза 1 секунд
                
        Serial.println("pravoitog)");
        motorControl(550, MOTOR1_IN, MOTOR1_PWM);  //povorot na pravo
        motorControl(550, MOTOR2_IN, MOTOR2_PWM);
        delay(450);
        stopMotors();
        delay(1000);  // Пауза 1 секунд
                
        Serial.println("vp2)");
        motorControl(800, MOTOR1_IN, MOTOR1_PWM);  // Оба колеса вперед
        motorControl(-800, MOTOR2_IN, MOTOR2_PWM);
        delay(600); //450
        stopMotors();
        delay(1000);  // Пауза 1 секунд
        
     } else if (command == "pribligenie") {

        Serial.println("pribligenie)");
        motorControl(800, MOTOR1_IN, MOTOR1_PWM);  // Оба колеса вперед
        motorControl(-800, MOTOR2_IN, MOTOR2_PWM);
        delay(80);
        stopMotors();
      

        


    }
}

void motorControl(int val, byte pinIN, byte pinPWM) {
  val = map(val, -1023, 1023, -255, 255); // Преобразование значения из диапазона -1023..1023 в -255..255

  if (val > 0) {  // Вперед
    analogWrite(pinPWM, val);
    digitalWrite(pinIN, LOW);
  } else if (val < 0) {  // Назад
    analogWrite(pinPWM, 255 + val); // 255 + отрицательное значение дает корректный PWM
    digitalWrite(pinIN, HIGH);
  } else if (val == 0) { // Стоп
    digitalWrite(pinIN, LOW);
    digitalWrite(pinPWM, LOW);
  }
}

void stopMotors() {
    motorControl(0, MOTOR1_IN, MOTOR1_PWM);
    motorControl(0, MOTOR2_IN, MOTOR2_PWM);

}
