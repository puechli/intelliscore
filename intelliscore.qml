//=============================================================================
//  MuseScore
//  Music Composition & Notation
//
//  Intelliscore Plugin
//
//  Copyright (C) 2024 - Aurélie Avanturier - Vander Elst Sidd - Puech Lilian
//
//  This program is free software; you can redistribute it and/or modify
//  it under the terms of the GNU General Public License version 2
//  as published by the Free Software Foundation and appearing in
//  the file LICENCE.GPL
//=============================================================================

import QtQuick 2.2
import MuseScore 3.0

MuseScore {
   version: "0.1"
   description: "This plugin scrolls automatically scores while hearing music instruments playing to permit music players having a synchronised and free-hand score scrolling."
   title: "Intelliscore"

   onRun: {
      Qt.quit();
   } // end onRun
}
