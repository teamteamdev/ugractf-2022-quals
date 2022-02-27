const socket = new WebSocket(`${window.location.href.replace('http', 'ws')}ws`);

const onClose = e => {
};

const onError = e => {
};

const onMessage = e => {
    try {
        data = JSON.parse(e.data);
    } catch (_) {
        // invalid data from server
        return;
    }

    if (data.flag !== undefined) {
        document.getElementById("flag").innerText = data.flag;
        if (data.flag.length >= 70) {
            document.getElementById("progress").className = "progress done";
        }
    }

    if (data.countdown !== undefined) {
        document.getElementById("timer").innerText = Math.floor(data.countdown / 10) + "" + (data.countdown % 10);
    }

    if (data.ciphertext !== undefined) {
        document.getElementById("ciphertext").innerText = data.ciphertext;
        document.getElementById("ciphertext").innerHTML = document.getElementById("ciphertext").innerHTML.replace(/Ж/g,
                                                          "<img class=eeee src=/static/err.svg style=width:1ch alt=err>");
        document.getElementById("seg-1").className = "segment active";
        document.getElementById("seg-2").className = "segment";
        document.getElementById("text").disabled = false;
        document.getElementById("submit-text").disabled = false;
        document.getElementById("key").disabled = true;
        document.getElementById("submit-key").disabled = true;
        document.getElementById("text").focus();
    }

    if (data.text !== undefined) {
        document.getElementById("text").value = data.text;
    }

    if (data.status !== undefined) {
        document.getElementById("text").parentNode.className = "field " + data.status;
        if (data.status) {
            document.getElementById("seg-1").className = "segment";
            document.getElementById("seg-2").className = "segment";
            document.getElementById("text").disabled = true;
            document.getElementById("submit-text").disabled = true;
            document.getElementById("key").disabled = true;
            document.getElementById("submit-key").disabled = true;
        } else {
            document.getElementById("seg-1").className = "segment";
            document.getElementById("seg-2").className = "segment active";
            document.getElementById("text").disabled = true;
            document.getElementById("submit-text").disabled = true;
            document.getElementById("key").disabled = false;
            document.getElementById("submit-key").disabled = false;
            document.getElementById("key").focus();
            document.getElementById("ciphertext").innerHTML = "&nbsp;";
            document.getElementById("text").value = "";
            document.getElementById("key").value = "";
        }
    }
};

socket.onclose = onClose;
socket.onerror = onError;
socket.onmessage = onMessage;

document.getElementById("key").focus();

document.getElementById("submit-text").onclick = e => {
    socket.send(JSON.stringify({"text": document.getElementById("text").value}));
};
document.getElementById("submit-key").onclick = e => {
    socket.send(JSON.stringify({"key": document.getElementById("key").value}));
};
document.getElementById("text").onkeypress = e => {
    if (e.keyCode == 13) {
        document.getElementById("submit-text").onclick(e);
    }
};
document.getElementById("key").onkeypress = e => {
    if (e.keyCode == 13) {
        document.getElementById("submit-key").onclick(e);
    }
};

window.setInterval(() => {
    let t = Math.max(0, parseInt(document.getElementById("timer").innerHTML) - 1);
    document.getElementById("timer").innerHTML = Math.floor(t / 10) + "" + (t % 10);
}, 1000);

