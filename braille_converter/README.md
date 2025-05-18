### MOTIVATION

  The motivation of the project is to make a braille educator for someone who has lost his vision for any reason and has to learn/practice braille.
--------------------------------------------------------------------------------------------------------------------------------------
### IDEA

  The idea of Edubra consists into a box that can recieve a text sent by the user, speak each letter of it and print the letter converted to braille in the user's finger, so then it is possible to memorize and practice his touch to braille. The user can send a file via the website with someone's help, and then, sit on some quiet place to use the device.
--------------------------------------------------------------------------------------------------------------------------------------
### SOFTWARE

  A website that can receive a file (docx, pdf, txt), extract its text, and send it to Raspberry Pi 4 via Wi-fi in the same server. With the text recieved by the site, the computer will create a sound file with each word in the text, so then it will be played before every word translated to braille. The Rasp has a code that interprets each letter on the file, translate it (based on a braille alphabet) and send a signal to hardware that makes a braille letter.
--------------------------------------------------------------------------------------------------------------------------------------
### HARDWARE

  6 servo motors that are connected with 6 pins that make the braille letter when get up. It has 4 buttons: two control the playback speed, one to pause the playback, and the other return a word. A speaker that pronounces every word or letter before the pins get activated.
--------------------------------------------------------------------------------------------------------------------------------------
