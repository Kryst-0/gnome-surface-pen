import QtQuick
import Quickshell
import Quickshell.Io
import qs.Commons as Commons
import qs.Ui as Ui

Ui.Panel {
    id: root
    moduleName: "krysto.surface-pen"
    ipcTarget: moduleName
    implicitWidth: button.implicitWidth
    implicitHeight: button.implicitHeight
    Commons.Translations { id: strings; directory: Qt.resolvedUrl("i18n") }
    property var config: ({single:"", double:"", hold:"", presentation:"auto"})
    property var apps: []
    property string gesture: "single"
    property bool connected: false
    property bool failed: false
    property var queue: []
    readonly property string helper: decodeURIComponent(Qt.resolvedUrl("control.py").toString().replace(/^file:\/\//,""))
    function request(args) { queue=queue.concat([args]); pump() }
    function pump() {
        if(worker.running || !queue.length)return
        var args=queue[0];queue=queue.slice(1)
        worker.command=["python3",helper].concat(args);worker.running=true
    }
    function set(key,value) { request(["set",key,value]); request(["state"]) }
    function appName(id) { for(var a of apps)if(a.id===id)return a.name;return strings.t("none") }
    onOpenedChanged: if(opened)request(["state"])
    Timer { interval:5000;repeat:true;running:root.opened;onTriggered:if(!worker.running && !root.queue.length)root.request(["state"]) }
    Process {
        id:worker
        onRunningChanged:if(!running)Qt.callLater(root.pump)
        stdout:StdioCollector {
            onStreamFinished: {
                try {
                    var d=JSON.parse(text);root.failed=!!d.error
                    if(d.settings){root.config=d.settings;root.apps=d.apps;root.connected=d.connected}
                }catch(e){root.failed=true}
            }
        }
    }
    Ui.BarIconButton {
        id:button;anchors.fill:parent;bar:root.bar
        text:"󰏪";tooltipText:strings.t("title")
        onPressed:root.toggle()
    }
    Ui.KeyboardPanel {
        owner:root;anchorItem:button;bar:root.bar;open:root.opened
        contentWidth:Commons.Style.space(480)
        contentHeight:Commons.Style.space(600)
        content:FocusScope {
            anchors.fill:parent
            Keys.onEscapePressed:root.close()
            Flickable {
                anchors.fill:parent;clip:true
                contentWidth:width;contentHeight:column.implicitHeight
                boundsBehavior:Flickable.StopAtBounds
            Column {
                id:column;width:parent.width;spacing:Commons.Style.space(10)
                Label { text:strings.t("title");font.pixelSize:Commons.Style.space(24) }
                Label { width:parent.width;text:strings.t(root.connected?"connected":"disconnected") }
                Row {
                    spacing:Commons.Style.space(6)
                    Repeater {
                        model:["single","double","hold"]
                        Ui.Button {
                            required property string modelData
                            text:strings.t(modelData);selected:root.gesture===modelData
                            onClicked:root.gesture=modelData
                        }
                    }
                }
                Label { width:parent.width;text:root.appName(root.config[root.gesture]) }
                Label { width:parent.width;text:strings.t("choose") }
                Ui.TextField { id:search;width:parent.width;placeholderText:strings.t("search");maximumLength:100 }
                Ui.Button { text:strings.t("none");onClicked:root.set(root.gesture,"") }
                ListView {
                    width:parent.width;height:Commons.Style.space(210);clip:true
                    model:root.apps.filter(a=>a.name.toLowerCase().includes(search.text.toLowerCase()))
                    delegate:Rectangle {
                        required property var modelData
                        width:ListView.view.width;height:Commons.Style.space(34)
                        color:mouse.containsMouse?Commons.Color.accent:"transparent"
                        Label { anchors.fill:parent;verticalAlignment:Text.AlignVCenter;text:modelData.name;elide:Text.ElideRight }
                        MouseArea { id:mouse;anchors.fill:parent;hoverEnabled:true;onClicked:root.set(root.gesture,modelData.id) }
                    }
                }
                Row {
                    spacing:Commons.Style.space(6)
                    Repeater {
                        model:["auto","on","off"]
                        Ui.Button {
                            required property string modelData
                            text:strings.t(modelData);selected:root.config.presentation===modelData
                            onClicked:root.set("presentation",modelData)
                        }
                    }
                }
                Label { width:parent.width;text:strings.t("hint");font.pixelSize:Commons.Style.font.caption }
                Label { visible:root.failed;text:strings.t("error") }
                Row {
                    spacing:Commons.Style.space(8)
                    Ui.Button { text:strings.t("bluetooth");onClicked:{root.close();Quickshell.execDetached(["omarchy-shell","shell","toggle","omarchy.bluetooth"])} }
                    Ui.Button { text:strings.t("close");onClicked:root.close() }
                }
            }
            }
        }
    }
    component Label:Text {
        textFormat:Text.PlainText
        color:Commons.Color.foreground
        font.family:Commons.Style.font.family
        font.pixelSize:Commons.Style.font.body
        wrapMode:Text.Wrap
    }
}
