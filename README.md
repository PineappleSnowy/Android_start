# 文件结构

favicon.ico、favicon.png：图标

index.html：html 前端代码

index.css：渲染 html 网页的样式文件

manifest.json：使网页能够被下载为桌面应用（PC端或手机均可）

sw.js：Service Worker 在网页已经关闭的情况下还可以运行, 用来实现页面的缓存和离线



****



**与传统 html 不同的代码：**

```html
<head>
    ...
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    ...
    <link rel="manifest" href="manifest.json" />
</head>
<body>
    ...
    <script src="./sw.js"></script>
</body>
```

