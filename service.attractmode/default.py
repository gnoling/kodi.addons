
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with XBMC; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html

import xbmc,xbmcgui
import subprocess,os
import random
import xbmcaddon, xbmcvfs
addon = xbmcaddon.Addon("service.attractmode")
PATH = addon.getAddonInfo('path')
RESOURCES_PATH = xbmc.translatePath( os.path.join( PATH, 'resources' ) ).decode('utf-8')
MEDIA_PATH = xbmc.translatePath( os.path.join( RESOURCES_PATH, 'media' ) ).decode('utf-8')
PLAYED_TRAILERS = False
VIDTYPES = ('.webm', '.mkv', '.flv', '.vob', '.ogv', '.ogg', '.ogm', '.drc', '.gif', '.gifv', '.mng', '.avi', '.mov', '.qt', '.wmv', '.yuv', '.rm', '.rmvb', '.asf', '.mp4', '.m4v', '.m4p', '.mpg', '.mp2', '.mpeg', '.mpe', '.mpv', '.svi', '.3gp', '.3g2', '.mxf', '.roq', '.nsv')

def getVideos(DIR):
	LIST = []
	if DIR.startswith(('smb://', 'nfs://', 'upnp://', 'ftp://')):
		dirs, files = xbmcvfs.listdir(DIR)
		for file in files:
			if file.lower().endswith(VIDTYPES):
				LIST.append(os.path.join( DIR, file ))
		for dir in dirs:
			LIST.extend(list(getVideos(os.path.join( DIR, dir ))))
	else:
		for root, dir, files in os.walk(DIR):
			for file in files:
				if file.endswith(VIDTYPES):
					LIST.append(os.path.join( root, file ))
	return LIST

def attractMode():
	VIDEOS  = addon.getSetting('videos').decode('utf-8')
	BUMPERS = addon.getSetting('bumpers').decode('utf-8')
	BSTART  = addon.getSetting('bstart')
	BFREQ   = int(addon.getSetting('bfreq'))
	BCROP   = int(addon.getSetting('bcrop'))
	xbmc.log('Loading bumper items')
	bumperItems  = list(getVideos(BUMPERS))
	xbmc.log('Loading video items')
	attractItems = list(getVideos(VIDEOS))
	playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
	playlist.clear()
	random.shuffle(bumperItems)
	random.shuffle(attractItems)
	if BSTART == 'true':
		C = 0
		while C < BCROP:
			I = bumperItems.pop(0)
			bumperItems.append(I)
			xbmc.log('Adding bumper %s to playlist' % I)
			playlist.add(url=I)
			C += 1
	A = 0
	for item in attractItems:
		if A == BFREQ:
			A = 0
			C = 0
			while C < BCROP:
				I = bumperItems.pop(0)
				bumperItems.append(I)
				xbmc.log('Adding bumper %s to playlist' % I)
				playlist.add(url=I)
				C += 1
		xbmc.log('Adding video %s to playlist' % item)
		playlist.add(item)
		A += 1
	xbmc.executebuiltin("xbmc.PlayerControl(RepeatAll)")
	xbmc.Player().play(playlist)
	while(not xbmc.abortRequested):
		if xbmc.Player().isPlayingVideo:
			TIMEOUT = int(addon.getSetting('idle_timeout'))*60
			IDLE_TIME = xbmc.getGlobalIdleTime()
			if IDLE_TIME < TIMEOUT:
				xbmc.log('Exiting attract mode')
				xbmc.executebuiltin('xbmc.PlayerControl(Stop)')
				xbmc.executebuiltin("xbmc.PlayerControl(RepeatOff)")
				break
		xbmc.sleep(1000)

class blankScreen(xbmcgui.Window):
	def __init__(self):
		pass

bs = blankScreen()
IDLE_TIME = 0
while(not xbmc.abortRequested ):
	if xbmc.getGlobalIdleTime() <= 5:
		IDLE_TIME = 0
	TIMEOUT = int(addon.getSetting('idle_timeout'))*60
	if IDLE_TIME < TIMEOUT:
		PLAYED_TRAILERS = False
		del bs
		bs = blankScreen()
	if IDLE_TIME > TIMEOUT:
		if not xbmc.Player().isPlaying():
			if not PLAYED_TRAILERS:
				PLAYED_TRAILERS = True
				bs.show()
				attractMode()
	if xbmc.Player().isPlaying():
		IDLE_TIME=0
	else:
		IDLE_TIME = IDLE_TIME + 1
	xbmc.sleep(1000)
