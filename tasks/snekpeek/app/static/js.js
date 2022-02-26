var direction = "U";
var timer;

const TICK = 250;

const socket = new WebSocket(`${window.location.href.replace('http', 'ws')}ws`);

const err = text => {
    if (document.getElementById("err").style.display == "none") {
        document.getElementById("errtext").innerText = text;
        document.getElementById("err").style.display = "block";
    }
};

const onClose = e => {
    err("Connection closed");
};

const onError = e => {
    err("Unknown server error");
};

const onMessage = e => {
    if (!timer) {
        timer = window.setInterval(advance, TICK);
    }
    try {
        data = JSON.parse(e.data);
    } catch (_) {
        err("Invalid data received from server");
    }
    document.getElementById("score").innerText = data.score;
    let els = document.getElementsByClassName("element");
    for (let i = 0; i < data.size; ++i) {
        for (let j = 0; j < data.size; ++j) {
            els[j * data.size + i].className = "element";
        }
    }
    if (data.target) {
        els[data.target[1] * data.size + data.target[0]].className = "element t";
    }
    if (data.head) {
        els[data.head[1] * data.size + data.head[0]].className = "element h";
    }

    d = [data.head[0], data.head[1]];
    for (let i = 0; i < data.tail.length; ++i) {
        if (data.tail[i] == "U") {
            --d[1];
        } else if (data.tail[i] == "L") {
            --d[0];
        } else if (data.tail[i] == "D") {
            ++d[1];
        } else if (data.tail[i] == "R") {
            ++d[0];
        } else {
            err("Invalid data received from server");
        }
        els[d[1] * data.size + d[0]].className = "element s";
    }

    if (data.error) {
        err(data.error);
    }
};

advance = () => {
    socket.send(direction);
}

window.onkeydown = e => {
    //    38
    // 37 40 39
    if (document.getElementById("err").style.display != "none") {
        return true;
    }
    if (e.keyCode == 38) {
        direction = "U";
    }
    if (e.keyCode == 37) {
        direction = "L";
    }
    if (e.keyCode == 40) {
        direction = "D";
    }
    if (e.keyCode == 39) {
        direction = "R";
    }
    advance();
    if (timer) {
        window.clearInterval(timer);
    }
    timer = window.setInterval(advance, TICK);
};

socket.onclose = onClose;
socket.onerror = onError;
socket.onmessage = onMessage;
