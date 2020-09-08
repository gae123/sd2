//
//  core.swift
//  sd2ui
//
//  Copyright © 2020 SiteWare Corp. All rights reserved.
//

import Foundation

private func executeShellCommand(command: String) -> Int32 {
    let process = Process()
    process.launchPath = "/bin/bash"
    process.arguments = [
        "-c",
        command
    ]
    process.launch()
    process.waitUntilExit()
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
