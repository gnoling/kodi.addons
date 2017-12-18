# -*- coding: utf-8 -*-

import xbmc, xbmcgui, os

if __name__ == '__main__':
  file = xbmc.getInfoLabel('ListItem.Trailer')
  xbmc.Player().play(file)
