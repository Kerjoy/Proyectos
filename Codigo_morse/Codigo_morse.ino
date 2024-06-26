const int ledPin = 2; // Pin donde está conectado el LED
const int duracionPunto = 200; // Duración del punto en milisegundos
const int duracionLinea = duracionPunto * 3; // Duración de la raya en milisegundos
const int duracionEntrePuntosRayas = duracionPunto; // Espacio entre puntos y rayas
const int duracionEntreLetras = duracionPunto * 3; // Espacio entre letras
const int espacioPalabras = duracionPunto * 7; // Espacio entre palabras

// Mapa de código Morse
const char* morseCode[] = {
  ".-", "-...", "-.-.", "-..", ".", "..-.", "--.", "....", "..", ".---", 
  "-.-", ".-..", "--", "-.", "---", ".--.", "--.-", ".-.", "...", "-", 
  "..-", "...-", ".--", "-..-", "-.--", "--.."
};

void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char caracterEntrante = Serial.read();
    if (caracterEntrante == ' ') {
      delay(espacioPalabras); // Espacio entre palabras
    } else {
      String morse = charToMorse(toupper(caracterEntrante));
      Serial.println(caracterEntrante);
      for (int i = 0; i < morse.length(); i++) {
        if (morse[i] == '.') {
          digitalWrite(ledPin, HIGH);
          delay(duracionPunto);
        } else if (morse[i] == '-') {
          digitalWrite(ledPin, HIGH);
          delay(duracionLinea);
        }
        digitalWrite(ledPin, LOW);
        delay(duracionEntrePuntosRayas);
      }
      delay(duracionEntreLetras - duracionEntrePuntosRayas); // Espacio entre letras
    }
  }
}

String charToMorse(char c) {
  if (c >= 'A' && c <= 'Z') {
    return morseCode[c - 'A'];
  } else {
    return "";
  }
}
