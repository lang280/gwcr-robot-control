// 定义创建websocket
// 提取当前URL的协议部分
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
// 提取主机名
const host = window.location.hostname;
// 定义WebSocket的路径, 如果需要的话
const path = ''; // 如果WebSocket服务器就在根路径上, 你可以将其留空
// 从html获得websocket端口
const port = window.serverPort_websocket;
// 拼接字符串以形成完整的WebSocket URL
const websocketURL = protocol + '//' + host + path + port;

// 创建WebSocket连接
const socket = new WebSocket(websocketURL);

console.log("socket created")

// 速度参数
const speed_slider = document.getElementById('slider_speed');
const speed_display = document.getElementById('value_slider_speed');
// 转向参数
const steering_slider = document.getElementById('slider_steering');
const steering_display = document.getElementById('value_slider_steering');
// 吸力参数
const suction_slider = document.getElementById('slider_suction');
const suction_display = document.getElementById('value_slider_suction');

// 上下左右键
const button_forward = document.getElementById('forward');
const button_backward = document.getElementById('backward');
const button_turn_left = document.getElementById('turn_left');
const button_turn_right = document.getElementById('turn_right');

// 事件：上键按下(鼠标)
button_forward.addEventListener('mousedown', function() {
    // 向服务器发送滑块值
    socket.send(`${speed_slider.value}|${'-'}|${'-'}`);
});

// 事件：上键松开(鼠标)
button_forward.addEventListener('mouseup', function() {
    // 向服务器发送滑块值
    socket.send(`${0}|${'-'}|${'-'}`);
});

// 事件：下键按下(鼠标)
button_backward.addEventListener('mousedown', function() {
    // 向服务器发送滑块值
    socket.send(`${-speed_slider.value}|${'-'}|${'-'}`);
});

// 事件：下键松开(鼠标)
button_backward.addEventListener('mouseup', function() {
    // 向服务器发送滑块值
    socket.send(`${0}|${'-'}|${'-'}`);
});

// 事件：左键按下(鼠标)
button_turn_left.addEventListener('mousedown', function() {
    // 向服务器发送滑块值
    socket.send(`${'-'}|${-steering_slider.value}|${'-'}`);
});

// 事件：左键松开(鼠标)
button_turn_left.addEventListener('mouseup', function() {
    // 向服务器发送滑块值
    socket.send(`${'-'}|${0}|${'-'}`);
});

// 事件：右键按下(鼠标)
button_turn_right.addEventListener('mousedown', function() {
    // 向服务器发送滑块值
    socket.send(`${'-'}|${steering_slider.value}|${'-'}`);
});

// 事件：右键松开(鼠标)
button_turn_right.addEventListener('mouseup', function() {
    // 向服务器发送滑块值
    socket.send(`${'-'}|${0}|${'-'}`);
});

// 事件：上键按下(触屏)
button_forward.addEventListener('touchstart', function() {
    // 向服务器发送滑块值
    socket.send(`${speed_slider.value}|${'-'}|${'-'}`);
});

// 事件：上键松开(触屏)
button_forward.addEventListener('touchend', function(event) {
    // 阻止默认行为(click)
    event.preventDefault();
    // 向服务器发送滑块值
    socket.send(`${0}|${'-'}|${'-'}`);
});

// 事件：下键按下(触屏)
button_backward.addEventListener('touchstart', function() {
    // 向服务器发送滑块值
    socket.send(`${-speed_slider.value}|${'-'}|${'-'}`);
});

// 事件：下键松开(触屏)
button_backward.addEventListener('touchend', function(event) {
    // 阻止默认行为(click)
    event.preventDefault();
    // 向服务器发送滑块值
    socket.send(`${0}|${'-'}|${'-'}`);
});

// 事件：左键按下(触屏)
button_turn_left.addEventListener('touchstart', function() {
    // 向服务器发送滑块值
    socket.send(`${'-'}|${-steering_slider.value}|${'-'}`);
});

// 事件：左键松开(触屏)
button_turn_left.addEventListener('touchend', function(event) {
    // 阻止默认行为(click)
    event.preventDefault();
    // 向服务器发送滑块值
    socket.send(`${'-'}|${0}|${'-'}`);
});

// 事件：右键按下(触屏)
button_turn_right.addEventListener('touchstart', function() {
    // 向服务器发送滑块值
    socket.send(`${'-'}|${steering_slider.value}|${'-'}`);
});

// 事件：右键松开(触屏)
button_turn_right.addEventListener('touchend', function(event) {
    // 阻止默认行为(click)
    event.preventDefault();
    // 向服务器发送滑块值
    socket.send(`${'-'}|${0}|${'-'}`);
});

// 禁止默认的触摸行为，如滑动、双击缩放等
document.addEventListener('touchstart', function(e) {
    // 如果触摸事件的目标是滑块类型的input，不阻止默认行为
    if (e.target.type !== 'range') {
        e.preventDefault();
    }
}, { passive: false });

document.addEventListener('touchmove', function(e) {
    // 如果触摸事件的目标是滑块类型的input，不阻止默认行为
    if (e.target.type !== 'range') {
        e.preventDefault();
    }
}, { passive: false });

document.addEventListener('touchend', function(e) {
    // 如果触摸事件的目标是滑块类型的input，不阻止默认行为
    if (e.target.type !== 'range') {
        e.preventDefault();
    }
}, { passive: false });

document.addEventListener('touchcancel', function(e) {
    e.preventDefault();
}, { passive: false });

document.addEventListener('gesturestart', function(e) {
    e.preventDefault();
}, { passive: false });

document.addEventListener('gesturechange', function(e) {
    e.preventDefault();
}, { passive: false });

document.addEventListener('gestureend', function(e) {
    e.preventDefault();
}, { passive: false });


// 事件: WebSocket 对象的连接成功建立时
// 确保socket.send不会在WebSocket连接前被触发
socket.onopen = function(event) {
    console.log("Connected to WebSocket server.");
};

// 事件：速度滑块被拖动时
speed_slider.addEventListener('input', function() {
    // 更新界面数据显示
    speed_display.innerText = "Speed: " + speed_slider.value;
});

// 事件：转向滑块被拖动时
steering_slider.addEventListener('input', function() {
    // 更新界面数据显示
    steering_display.innerText = "Steer: " + steering_slider.value;
});

// 事件：吸力滑块被拖动时
suction_slider.addEventListener('input', function() {
    // 更新界面数据显示
    suction_display.innerText = "Suction: " + suction_slider.value;
    // 向服务器发送滑块值
    socket.send(`${'-'}|${'-'}|${suction_slider.value}`);
});

// 事件: DOMContentLoaded
// 确保在尝试访问 DOM 元素或初始化 WebSocket 连接之前, HTML 完文档已经完全加载和解析
document.addEventListener('DOMContentLoaded', function() {
    console.log("完成初始化");
});
