//
//  core.swift
//  sd2ui
//
//  Copyright © 2020 SiteWare Corp. All rights reserved.
//

import Foundation
import os.log

private func executeShellCommand(command: String) -> Int32 {
    os_log("Executing '%{public}@'", command)
    let process = Process()
    process.executableURL = URL(fileURLWithPath: "/bin/bash")
    process.arguments = [
        "-l",
        "-c",
        command
    ]
    do {
        try process.run()
    }  catch {
        os_log("Error starting process")
        return -1;
    }
    process.waitUntilExit()
    os_log("Returned '%{public}@'", process.terminationStatus)
    return process.terminationStatus
    
}

func isDaemonRunning() -> Bool {
    return executeShellCommand(
        command: "ps -efwww | egrep -v 'grep|sd2ui' |  grep '/sd2'"
    ) == 0
}

func stopServer() {
    _ = executeShellCommand(
        command: "sd2 halt"
    )
}

func startServer() {
    _ = executeShellCommand(
        command: "sd2"
    )
}

func startContainers() {
    _ = executeShellCommand(
        command: "sd2 docker"
    )
}

func startRsync() {
    _ = executeShellCommand(
        command: "sd2 rsync"
    )
}
