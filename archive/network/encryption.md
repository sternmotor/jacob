Zunächst soll die Grundidee des Diffie-Hellman-Merkle-Schlüsselaustauschs anhand von „Farbmischen“ anschaulich dargestellt werden, wie es die Illustration links veranschaulicht. In Wirklichkeit wären die Farben Zahlen und das Mischen von Farben entspräche der diskreten Exponentialfunktion.

Das Mischen von Farben wird hier als eine Einwegfunktion aufgefasst: Es ist „leicht“, zwei oder mehrere verschiedene Farben zu mischen. Die Umkehrung, das Zerlegen einer Farbmischung in ihre ursprünglichen Farb-Komponenten, ist jedoch sehr aufwändig, das heißt nicht effizient durchführbar.

Alice und Bob einigen sich zunächst öffentlich auf eine gemeinsame Farbe (im Beispiel Gelb). Außerdem wählt jeder der beiden Kommunikationspartner für sich eine geheime Farbe (Alice Orange und Bob Türkis). Bob und Alice mischen nun jeweils die gemeinsame Farbe mit ihrer geheimen Farbe. Im Beispiel entsteht dabei für Alice Beige und für Bob Graublau. Diese Farbmischungen tauschen Alice und Bob nun über die abhörbare Leitung aus. Einer potenziellen Lauscherin Eve ist es nicht effizient möglich, aus den öffentlichen Informationen (gelb, beige, graublau) auf die geheimen Farben von Alice und Bob zu schließen.

In einem letzten Schritt mischen nun Alice und Bob die Farbmischung ihres Gegenübers mit ihrer eigenen geheimen Farbe. Daraus entsteht wiederum eine neue Farbe (im Beispiel Ockerbraun), die für beide Kommunikationspartner gleich ist (gelb + orange + türkis = gelb + türkis + orange = ockerbraun). Somit haben Alice und Bob eine gemeinsame geheime Farbe. Für Eve ist es unmöglich, diese herauszufinden, da sie Alices und Bobs geheime Farbzutaten nicht kennt.

bild: media/Diffie-Hellman_Key_Exchange.png
