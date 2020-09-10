//
//  AppDelegate.swift
//  sd2ui
//
//  Copyright © 2020 SiteWare Corp. All rights reserved.
//

import Cocoa
import SwiftUI

@NSApplicationMain
class AppDelegate: NSObject, NSApplicationDelegate {

    var statusBarItem: NSStatusItem!
    var startStopMenuItem: NSMenuItem!
    var rsyncMenuItem: NSMenuItem!
    var dockerMenuItem: NSMenuItem!
    var timer: Timer!

    func applicationDidFinishLaunching(_ aNotification: Notification) {

        let statusBarMenu = NSMenu(title: "sd2 Bar Menu")
        
        // Create the status item
        statusBarItem = NSStatusBar.system.statusItem(withLength: CGFloat(NSStatusItem.variableLength))
        
        statusBarItem.menu = statusBarMenu
        
        if let button = self.statusBarItem.button {
            button.image = NSImage(named: "Icon")
        }
        
        startStopMenuItem = statusBarMenu.addItem(
            withTitle: "Stop",
            action: #selector(AppDelegate.stopServerHelper),
            keyEquivalent: "")
        
        statusBarMenu.addItem(NSMenuItem.separator())
        
        rsyncMenuItem = statusBarMenu.addItem(
        withTitle: "Force Rsync",
        action: #selector(AppDelegate.startRsyncHelper),
        keyEquivalent: "")
        
        dockerMenuItem = statusBarMenu.addItem(
        withTitle: "Start Containers",
        action: #selector(AppDelegate.startContainersHelper),
        keyEquivalent: "")
        
        statusBarMenu.addItem(NSMenuItem.separator())
        
        statusBarMenu.addItem(
            withTitle: "Quit",
            action: #selector(AppDelegate.quit),
            keyEquivalent: "")
        
        // Periodically check daemon status and update UI
        checkDaemonStatusAndUpdateUI()
        timer = Timer.scheduledTimer(timeInterval: 5.0, 
                                     target: self, 
                                     selector: #selector(checkDaemonStatusAndUpdateUI), 
                                     userInfo: nil, 
                                     repeats: true)
    }
    
    @objc func quit() {
        exit(0)
    }
    
    @objc func stopServerHelper() {
        stopServer()
    }
    
    @objc func startServerHelper() {
        startServer()
    }
    
    @objc func startRsyncHelper() {
        startRsync()
    }
    
    @objc func startContainersHelper() {
        startContainers()
    }
    
    @objc func checkDaemonStatusAndUpdateUI() {
        let daemonRunning = isDaemonRunning()
        if let button = self.statusBarItem.button {
            if daemonRunning && button.contentTintColor != NSColor.green {
                button.contentTintColor = NSColor.green
                startStopMenuItem.title = "Stop sd2"
                startStopMenuItem.action = #selector(AppDelegate.stopServerHelper)
                dockerMenuItem.isHidden = false
                rsyncMenuItem.isHidden = false
            }
            if !daemonRunning && button.contentTintColor != NSColor.red {
                button.contentTintColor = NSColor.red
                startStopMenuItem.title = "Start sd2"
                startStopMenuItem.action = #selector(AppDelegate.startServerHelper)
                dockerMenuItem.isHidden = true
                rsyncMenuItem.isHidden = true
            }
        }
    }
    

    func applicationWillTerminate(_ aNotification: Notification) {
        // Insert code here to tear down your application
        timer?.invalidate()
        timer = nil
    }


}

