#!/usr/bin/env python
# -*- coding: utf-8 -*-

PACKAGE = 'alfred_tts_linux'
NODE = 'tts'

SUB_DISPLAY = "robotsay"
TMP_FILE = "/tmp/test.wav"

voice = 'fr-FR' #'fr-FR' "en-US"

# Import after printing usage for speed.
import roslib;
roslib.load_manifest( PACKAGE )
roslib.load_manifest( 'media_msgs' )
roslib.load_manifest( 'sound_play' )
import rospy

from media_msgs.msg import *
from sound_play.msg import SoundRequest
from sound_play.libsoundplay import SoundClient

import subprocess

import sys, os, errno
reload( sys )
sys.setdefaultencoding( "utf-8" )

def execute( cmd ):
    p = subprocess.Popen( cmd, shell = True, stderr = subprocess.PIPE )
    while True:
        out = p.stderr.read( 1 )
        if out == '' and p.poll() != None:
            break
        if out != '':
            sys.stdout.write( out )
            sys.stdout.flush()


class Say():
    
    
    def __init__( self ):
        """ Node Constructor """
        
        rospy.loginfo( 'Start %s node...', NODE )
        rospy.on_shutdown( self.__on_shutdown )
        
        self.soundhandle = SoundClient()
        rospy.sleep( 1 )
        
        rospy.loginfo( 'Start Topics (publishers/subscribers)...' )
        self.sub = rospy.Subscriber( SUB_DISPLAY, Command, self.__say )
        
        rospy.loginfo( 'Start main loop...' )
        rospy.spin()
    
    def __say( self, data ):
        rospy.logdebug( '%s say : %s', data.context.who, data.subject )
        
        # remove old file
        self.silentremove( TMP_FILE )
        
        # Generate TTS
        cmd = 'pico2wave -l %s -w /tmp/test.wav "%s " > /dev/null' % ( voice, data.subject, )
        #rospy.loginfo(cmd)
        execute( cmd )
        
        # Play by robotout
        self.soundhandle.playWave( TMP_FILE )
    
    def __on_shutdown( self ):
        rospy.sleep( 1 )
    
    def silentremove( self, filename ):
        try:
            os.remove( filename )
        except OSError as e: # this would be "except OSError, e:" before Python 2.6
            if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
                raise # re-raise exception if a different error occured

if __name__ == '__main__':
    rospy.init_node( NODE ) #, anonymous=True
    try:
        node = Say()
    except rospy.ROSInterruptException, e: 
        pass
