# Homicidio en el Atlántico (MSX): curiosidades

## La historia y sus guiños

- El barco es el **SS Bourgogne** (Borgoña) de la «Cía Francesa de Transportes», 1937. Las suites se llaman como vinos de Borgoña: **Chambertin** y **Clos-Vougeot**.
- El científico al que persiguen es el profesor **Alan «Turning»** (Alan Turing), que quiere llevarse a EE. UU. el trabajo con su «profesor Von Neuman». En la maleta hay un microfilm de la máquina **ENIGMA** y la combinación es **ADA** (Ada Lovelace, la hija de Lord Byron, autor de *Childe Harold's Pilgrimage*: «piensa en la niña del autor de la peregrinación…», dice Pellton).
- El ascensor es de la marca **«LEIBNITZ & BOOLE»** y su autodiagnóstico es un número en binario: `** *   * **   * ` = 1101000101100010 = **53602**.
- El polizón va a Estados Unidos porque le han ofrecido trabajo de representante en **IBM**.
- La novela que dice leer el ciego es *El falso suicidio de Sir Atmos **Microsoftkis***, «por Gahete y Fouquet». El MSX llevaba el BASIC de Microsoft.
- El ciego se llama **William Allison**, casi como la grafista del juego, Marie-Anne Alison. Es en realidad John Wade, el individuo peligroso que busca la policía de Nueva York en el mensaje de morse.
- El capitán **Kappock** grita los insultos del capitán Haddock de Tintín: «¡Ornithorynque! ¡Bachi-Bou-Zouk! ¡Antropófago! ¡Ectoplasma! ¡Coloquíntida! ¡Ostrógodo!». Le han cambiado 12 cajas de whisky por Canada Dry, cuando pensaba venderlas en EE. UU. con la ley seca.
- La orquesta **Ray Boulinat** recuerda a la de Ray Ventura. A la estrella Pamela Carington le han robado el collar de perlas «que le regaló John Ford».
- La última pregunta del test es **«¿Cuál es la edad del capitán?»**, la broma clásica francesa de Flaubert (un problema sin datos para sacar la respuesta). El test solo pide 2 cifras que sumen 8: 44, 35, 17, 80...
- Las dos muertes: Philippe de La Vallière (agente francés, el «aviador») aparece estrangulado; el alemán Otto Kempfer aparece en el frigorífico con un tiro que parece suicidio. El doctor dice que fue un suicidio; el libro del ciego dice lo contrario.

## El juego venía con una caja de pistas

*Meurtres sur l'Atlantique* se vendía con un dossier de objetos de verdad: sobre, microfilm, telegrama, fotos rotas, cartas… El juego remite a ellos: «(MIRAR LA FOTO)», «UN SOBRE (ÁBRELO)», y la versión francesa marca con `*` cada objeto que estaba en la caja. Varias preguntas del test (la estrella más brillante, lo que se ve en el microfilm, la hora del radiotelegrama, lo que representa la foto rota) **solo se pueden contestar con ese material**. Sin la caja, las respuestas las saqué de las sumas ASCII del TEST y las comprobé en el juego.

## Fallos de la versión española

1. **El morse se corta**. Al escuchar el mensaje de la radio (A77, S), el programa traduce cada letra con `ASC(letra)-64`. Los espacios dan un número negativo (repiten la letra anterior) y la **Ñ de «BORGOÑA»** pide más DATA de los que hay: «Out of DATA», que el gestor de errores muestra como «ATENCIÓN ERROR DE CASSETTE». El mensaje nunca llega a «BAJO EL NOMBRE DE AL...». En francés iba sin espacios ni eñes (SURBOURGOGNE).
2. **La maleta dice «CORRECTO...» cuando fallas**: la traducción de «RÉPONSE FAUSSE...» se comió el «NO».
3. **El mensaje del test perfecto no sale nunca**: `R=R/2: ON R GOSUB ...` con 15 preguntas da como mucho 7,5 → mensaje 7. El 8.º («¡MUY BIEN! ¡NO HAY FALTA NINGUNA!») es inalcanzable. Pasa igual en francés; **el alemán lo arregla** con `IF R=15 THEN GOSUB 320`.
4. Erratas: «DEMASADIO» (dos veces), «CONCIENCA», «FEMININOS», «NON AUTORIZADO» (francés a medias) y «¡AI! ¡EL ASCENSOR NO FUNCIONA!».
5. MSA1 pide `TRIMMSA`, pero en la cinta el fichero se llama `TRIMMS`: funciona porque la cinta solo compara 6 letras.

## Restos y detalles escondidos

- Los dos muertos tienen testimonio en la cinta aunque el juego no deja interrogarlos («¿AÚN NO ERES CAPAZ DE HACER HABLAR A LOS MUERTOS?»). El de La Vallière (TEM13) dice «Vacío por pamena» y el de Kempfer (TEM22) «Esto me divierte».
- Los comentarios del BASIC están en francés también en la cinta española (`INITIALISATION DE L'ECRAN`, `BOUCLE PRINCIPALE`, `APPEL DE L'ASCENSEUR`, `FOUILLE`…).
- La línea 730 (`'IF T<>(Y1+E)/2 THEN 810`) está anulada: la avería del ascensor iba a darse en un puente concreto.
- En el fotógrafo (E65) se dibuja con LINE la grieta del escaparate encima del dibujo de la sala.
- Altman, el nazi, primero se niega («¡ME QUEJARÉ A MI GOBIERNO!»); si pulsas A le registras igual y el juego te felicita por no dejarte intimidar.
- El vigilante de los sollados y Marthe Granet se veían cada noche «debajo de la escalera del puente J».

## De los discos

- El disco francés lleva un `TEM1O.BIN` (con O) que es una copia exacta de `TEM10.BIN`, un error al copiar los ficheros. El disco alemán lo heredó: tiene su TEM10 en alemán y ese TEM1O en **francés**.
- El cargador del disco francés firma «PISANT & MEGA SOFT!» y toca los subslots (`POKE &HFFFF`) para que vaya en máquinas con slots expandidos.
- El alemán lo pasó a disco «MINIC Computing» el 18-3-1987, con rótulos en neerlandés, y la pantalla de título dice «MURDER ON THE ATLANTIC», en inglés.
- El alemán pregunta «¿QUIERE **GRABAR** EL ESTADO DE LA INVESTIGACIÓN?» (*speichern*) cuando en realidad lo que hace es **cargarlo**.
- El ETAT.BIN del disco francés es una partida guardada por alguien, con solo la radio desbloqueada.
