# Zergbot
Toto je port originál ZergBota z 2014, ktorého vtedy skódil Adam Dej, Syseľ (a možno niekto ďalší). Originál kód je na troch miestach:
* [Frontend na GDrive](https://drive.google.com/file/d/1FkCd3SrARQyyoSEE9EV90-EqlSeBD3Jv/view?usp=sharing)
* [Backend v tomto repe](https://github.com/trojsten/web/pull/1214)
* Skript, ktorý bežal interpreter na elementovi pri submite. Ten je asi stratený.

Snažil som sa nechytať toho frontendového kódu moc. Hlavná zmena je, že backendový interpreter beží rovno na webovom serveri. Je to funkcia `run_interpreter()` vo `views.py`.
