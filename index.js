// 对于导航元素的点击事件处理
function toggleDropdown(navtog) {
    navtog.classList.toggle('active');
}

document.getElementById('navtog').addEventListener('click', function () {
    toggleDropdown(this);
});

// 对于按钮的点击事件处理
function removeNavtogActive() {
    var navtogElement = document.getElementById('navtog');
    navtogElement.classList.remove('active');
}

document.getElementById('camera-button').addEventListener('click', removeNavtogActive);
document.getElementById('env-button').addEventListener('click', removeNavtogActive);
document.getElementById('install-button').addEventListener('click', removeNavtogActive);

const iframe = document.getElementById('nestedWebpage');
const cameraButton = document.getElementById('camera-button');
const envButton = document.getElementById('env-button');
const installButton = document.getElementById('install-button');

cameraButton.addEventListener('click', function () {
    iframe.src = 'https://159.75.84.38';
});
envButton.addEventListener('click', function () {
    iframe.src = 'https://162.14.97.177';
});

window.addEventListener('beforeinstallprompt', e => {
    e.preventDefault();

    // 下载按钮点击后显示安装弹窗
    installButton.addEventListener('click', () => {
        e.prompt();
    });
});