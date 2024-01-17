<h1 align="center">
  <br>
  <img src="https://github.com/shipt/opsml/blob/main/images/opsml-logo.png?raw=true"  width="400" height="400" alt="opsml logo"/>
  <br>
</h1>

<h2 align="center">Adding Quality Management to Machine Learning</h2>

<h1 align="center"><a href="https://thorrester.github.io/opsml-ghpages/">OpsML Documentation</h1>

[![Opsml](https://img.shields.io/badge/Opsml-v2-blueviolet?logo=data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjwhLS0gQ3JlYXRlZCB3aXRoIElua3NjYXBlIChodHRwOi8vd3d3Lmlua3NjYXBlLm9yZy8pIC0tPgoKPHN2ZwogICB2ZXJzaW9uPSIxLjEiCiAgIGlkPSJzdmcxIgogICB3aWR0aD0iMTQwLjMxMTIzIgogICBoZWlnaHQ9IjE0My4yMjI3OCIKICAgdmlld0JveD0iMCAwIDE0MC4zMTEyMyAxNDMuMjIyNzgiCiAgIHNvZGlwb2RpOmRvY25hbWU9ImdlYXItY29sb3Iuc3ZnIgogICBpbmtzY2FwZTp2ZXJzaW9uPSIxLjMuMiAoMDkxZTIwZSwgMjAyMy0xMS0yNSkiCiAgIHhtbG5zOmlua3NjYXBlPSJodHRwOi8vd3d3Lmlua3NjYXBlLm9yZy9uYW1lc3BhY2VzL2lua3NjYXBlIgogICB4bWxuczpzb2RpcG9kaT0iaHR0cDovL3NvZGlwb2RpLnNvdXJjZWZvcmdlLm5ldC9EVEQvc29kaXBvZGktMC5kdGQiCiAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CiAgPGRlZnMKICAgICBpZD0iZGVmczEiIC8+CiAgPHNvZGlwb2RpOm5hbWVkdmlldwogICAgIGlkPSJuYW1lZHZpZXcxIgogICAgIHBhZ2Vjb2xvcj0iI2ZmZmZmZiIKICAgICBib3JkZXJjb2xvcj0iIzAwMDAwMCIKICAgICBib3JkZXJvcGFjaXR5PSIwLjI1IgogICAgIGlua3NjYXBlOnNob3dwYWdlc2hhZG93PSIyIgogICAgIGlua3NjYXBlOnBhZ2VvcGFjaXR5PSIwLjAiCiAgICAgaW5rc2NhcGU6cGFnZWNoZWNrZXJib2FyZD0iMCIKICAgICBpbmtzY2FwZTpkZXNrY29sb3I9IiNkMWQxZDEiCiAgICAgc2hvd2dyaWQ9ImZhbHNlIgogICAgIGlua3NjYXBlOnpvb209IjIuOTc2NTYyNSIKICAgICBpbmtzY2FwZTpjeD0iNi43MTkxNjAxIgogICAgIGlua3NjYXBlOmN5PSI3Ni45MzQzODMiCiAgICAgaW5rc2NhcGU6d2luZG93LXdpZHRoPSIxOTIwIgogICAgIGlua3NjYXBlOndpbmRvdy1oZWlnaHQ9Ijg1MSIKICAgICBpbmtzY2FwZTp3aW5kb3cteD0iMTgwNSIKICAgICBpbmtzY2FwZTp3aW5kb3cteT0iMjUiCiAgICAgaW5rc2NhcGU6d2luZG93LW1heGltaXplZD0iMCIKICAgICBpbmtzY2FwZTpjdXJyZW50LWxheWVyPSJnMSIKICAgICBzaG93Z3VpZGVzPSJ0cnVlIiAvPgogIDxnCiAgICAgaW5rc2NhcGU6Z3JvdXBtb2RlPSJsYXllciIKICAgICBpbmtzY2FwZTpsYWJlbD0iSW1hZ2UiCiAgICAgaWQ9ImcxIgogICAgIHRyYW5zZm9ybT0idHJhbnNsYXRlKC02OS41NzQ4MDMsLTUyLjMwNDQ1OSkiPgogICAgPHBhdGgKICAgICAgIHN0eWxlPSJmaWxsOiMyY2NiNzQiCiAgICAgICBkPSJtIDEzNS4wMjA4MiwxOTUuNDM3NDYgYyAtMi4yMTE3LC0wLjA3NDIgLTQuNjA5MzcsLTAuMjI5MTggLTUuMzI4MTcsLTAuMzQ0NDYgLTEwLjQ0NzUyLC0xLjY3NTUgLTE5Ljc3ODY1LC01LjI1MDM0IC0yOC4zNDk4OSwtMTAuODYxMDggLTUuMjcxNzM3LC0zLjQ1MDg5IC0xMS4xMjQ2MjcsLTguNjg1OSAtMTUuMjkxNjI3LC0xMy42NzczMSAtMi40Njk0MywtMi45NTc5OSAtMi45MTYzNCwtMy41NjUzOCAtNS4yMjg2MSwtNy4xMDYyMiAtMi4xNDc0MSwtMy4yODgzNyAtMi40MTUyOSwtMy43NjgyOSAtNC4zODkyMywtNy44NjM0IC0xLjk4NDY0LC00LjExNzMzIC0zLjUzMjk5LC04LjI1ODkxIC00LjY3NjUsLTEyLjUwODg2IC0wLjEyMTM4LC0wLjQ1MTE0IC0wLjMzNTAxLC0xLjIzNTUxIC0wLjQ3NDczLC0xLjc0MzA0IC0wLjEzOTczLC0wLjUwNzUzIC0wLjM2MjY3LC0xLjQ3NjQ2IC0wLjQ5NTQ0LC0yLjE1MzE2IC0wLjEzMjc3LC0wLjY3NjcxIC0wLjM2MTMxLC0xLjgzMDE5IC0wLjUwNzg3LC0yLjU2MzMgLTAuNjQ1NzYsLTMuMjMwMDQgLTAuNzAzOTUsLTQuMjgxMDEgLTAuNzAzOTUsLTEyLjcxMzkyIDAsLTguNDA5MjggMC4wNjk2LC05LjY3ODIzIDAuNjk3MDQsLTEyLjcxMzkyIDAuMTUxNTMsLTAuNzMzMSAwLjM4MzY2LC0xLjg4NjU5IDAuNTE1ODQsLTIuNTYzMjkgMC4xMzIxOCwtMC42NzY3MSAwLjM1Nzk1LC0xLjY0NTY0IDAuNTAxNjksLTIuMTUzMTcgMC4xNDM3NSwtMC41MDc1MyAwLjMwODExLC0xLjE1MzQ4IDAuMzY1MjYsLTEuNDM1NDQgMC4wOTU5LC0wLjQ3MzA1IDAuMjgzNzYsLTEuMTg1NDQgMC43MzAxNiwtMi43NjgzNiAwLjE5MjU1LC0wLjY4Mjc3IDAuODY3ODgsLTIuNjMzMjEyIDEuMzQ5MDUsLTMuODk2MjEyIDAuMTcxODcsLTAuNDUxMTQgMC4zODI5MSwtMS4wMDQ4MSAwLjQ2ODk4LC0xLjIzMDM4IDAuOTg3NDQsLTIuNTg3ODMgMi42OTgzMSwtNi4xNzI5NCA0LjUwMTUyLC05LjQzMjkxIDAuOTIzMjUsLTEuNjY5MTIgMy4zMTYzMywtNS4yMzg2MTYgNC45NDkyNiwtNy4zODIyNzYgMi4yMzE0NSwtMi45MjkzNyAyLjkzNjQ4LC0zLjczMDQ1IDYuMzIyNTUsLTcuMTgzODkgMy4xMDg4MSwtMy4xNzA2NiA0LjI0MjkxLC00LjIyMzcgNS45MjE0MSwtNS40OTgxMiAwLjYxNzI5LC0wLjQ2ODY5IDEuMjEyODIsLTAuOTU0NjMgMS4zMjM0MSwtMS4wNzk4NiAwLjI0MDU2LC0wLjI3MjQzIDMuODg4ODA3LC0yLjg3MTU0IDUuMDIzNzI3LC0zLjU3OTA0IDEuMzQwNjUsLTAuODM1NzUgMS41OTkzMSwtMC45OTAzMSAxLjkxMjk0LC0xLjE0MzAzIDAuMTY1ODgsLTAuMDgwOCAwLjYzOTA4LC0wLjM2MTIyIDEuMDUxNTcsLTAuNjIzMjIgNC4zOTUxOSwtMi43OTE3IDEzLjg1OTc0LC02LjQwOTExIDE5Ljk1OTUyLC03LjYyODYzIDUuOTYzNjYsLTEuMTkyMzIgNy4wOTcxNywtMS4yOTYzMSAxNC4wMTYyMiwtMS4yODU4NiA3Ljg3MDQsMC4wMTE5IDkuODA0ODQsMC4xOTUxNiAxNS44NDE2NCwxLjUwMDg3IDIuNTEwMjYsMC41NDI5NSA3LjA4ODY3LDEuOTI5MTcgOS4yNzE5LDIuODA3MjggNi43ODYyNiwyLjcyOTQ5IDExLjc1NjM5LDUuNDMwOTMgMTYuNTY0Nyw5LjAwMzUyIDMuNjkyMjYsMi43NDMzNiA4LjUxODY4LDcuMTM0NjQgMTAuODg2NjQsOS45MDUxNCAwLjUzNjg0LDAuNjI4MDkgMS4zMjkxMywxLjU1MDg4IDEuNzYwNjQsMi4wNTA2MyAxLjgzMTM0LDIuMTIwOTcgNS44NDAwNyw3Ljg2NzI1NiA3LjA3MTQxLDEwLjEzNjQ4NiAyLjI1NTU1LDQuMTU2NzIgMy42NTcwNiw3LjExNiA0LjUxNTk5LDkuNTM1NDQgMC4xNDAxMywwLjM5NDc1IDAuMzY5OCwwLjk5NDU2IDAuNTEwMzcsMS4zMzI5MSAwLjM3MzIzLDAuODk4MzkgMS4yMjg3MSwzLjUzMTgzMiAxLjYwMzE1LDQuOTM1MDEyIDIuNDIwMzcsOS4wNyAyLjgxMjEyLDEyLjQzMTc2IDIuNjM4OTcsMjIuNjQ2MDIgLTAuMTA0NDksNi4xNjM5OCAtMC4yMDQwNCw3LjQxNTMzIC0wLjgzMjA3LDEwLjQ1ODIyIC0wLjE1MTMxLDAuNzMzMTEgLTAuMzgzMjUsMS44ODY1OSAtMC41MTU0NCwyLjU2MzMgLTAuMTMyMTgsMC42NzY3IC0wLjM1NDY1LDEuNjQ1NjMgLTAuNDk0MzcsMi4xNTMxNiAtMC4xMzk3MywwLjUwNzUzIC0wLjM1MzM2LDEuMjkxOSAtMC40NzQ3NCwxLjc0MzA0IC0xLjU4NzM0LDUuODk5NSAtNC44NDgzNCwxMy42ODM1IC03LjU1OTk1LDE4LjA0NTU3IC0xLjEzODQ3LDEuODMxNCAtMy42Nzg1Nyw1LjY0MTE2IC00LjIxNTcsNi4zMjI4OSAtNi4yNTY1OSw3Ljk0MDkyIC0xMi4xNDE0OCwxMy4zMTE5IC0xOS43MjA0MiwxNy45OTgyNyAtNS4wNTU5OSwzLjEyNjMzIC0xMS44ODYxMSw2LjE0ODk2IC0xNy4wOTAzNSw3LjU2MzI0IC0wLjMzMTc2LDAuMDkwMiAtMS4xNDYwNiwwLjMxNDgzIC0xLjgwOTU3LDAuNDk5MjcgLTIuMDE1NjYsMC41NjAzMSAtNi45MTY1OCwxLjUwMTg1IC05LjA0Nzg0LDEuNzM4MjMgLTIuNTc2NDIsMC4yODU3NSAtNy45NTE5MSwwLjM2NTQ5IC0xMy4wNjkwOSwwLjE5Mzg2IHogbSA4LjE2ODI2LC0zMC45OTI3MyBjIDEuMzY4ODcsLTAuNjQwNzMgMi4yNDExNSwtMS44NzM5MyAyLjk3MjMxLC00LjIwMjE4IDAuMjAyMzQsLTAuNjQ0MzIgMC42NDU3MSwtMS42NzkwMiAwLjk4NTI2LC0yLjI5OTMzIDAuMzM5NTUsLTAuNjIwMzIgMC43NjU5NiwtMS40MjE1MSAwLjk0NzU3LC0xLjc4MDQzIDAuMzA3MDMsLTAuNjA2ODEgMi4wMjM4MywtMi40MTAxOCAyLjcxMDA0LC0yLjg0NjcgMC4xNjU4OCwtMC4xMDU1MiAwLjQwMTY2LC0wLjM3NjQyIDAuNTIzOTYsLTAuNjAxOTkgMC4xOTM2NiwtMC4zNTcyMSAwLjQ2NjA1LC0wLjQxODA2IDIuMTExMTYsLTAuNDcxNjUgMi4zNjU0MywtMC4wNzcgNC40NjU5NCwwLjQ0NDgzIDcuMzc2NjEsMS44MzI3NSAxLjgzMzcyLDAuODc0MzkgMy4xNDEwNiwwLjk4MDc3IDQuMzg2MjIsMC4zNTY5MSAxLjA5MTAxLC0wLjU0NjYyIDMuMjg5MTQsLTIuNjgzNTcgNC4zMjMxOCwtNC4yMDI4NCAwLjYwODQzLC0wLjg5Mzk1IDAuNjgwMzYsLTEuMTQ0MDggMC42NzEyLC0yLjMzNDE1IC0wLjAwOCwtMS4wOTM3MSAtMC4xNDQzNiwtMS42MjczMyAtMC43NTc0OSwtMi45NzM0MiAtMC40MTA5OCwtMC45MDIyOCAtMC44MjM0NiwtMS43ODAwNCAtMC45MTY2MiwtMS45NTA1NyAtMC4wOTMyLC0wLjE3MDU0IC0wLjMzMjAzLC0wLjg2MjYzIC0wLjUzMDgzLC0xLjUzNzk4IC0wLjQyNTAzLC0xLjQ0Mzk0IC0wLjUxMzAxLC01LjI5NDUzIC0wLjEyOTksLTUuNjg1MjcgMC4xMjg2NiwtMC4xMzEyMiAwLjIzMzkzLC0wLjM1ODM0IDAuMjMzOTMsLTAuNTA0NjkgMCwtMC41NjQyOSAxLjQ4ODc5LC0yLjM0MDM1IDIuNjc2NzcsLTMuMTkzMjYgMS40MzAyNiwtMS4wMjY4NyAzLjk1NjQ5LC0yLjMxNzcyIDQuOTE0ODcsLTIuNTExNDEgMC45NTM2OSwtMC4xOTI3MyAyLjk3MTU5LC0xLjY0MDA3IDMuNDk4MTcsLTIuNTA5MDUgMC40MjAxOSwtMC42OTM0MSAwLjQ1MzY3LC0wLjk4MTMyIDAuNDQ1OTIsLTMuODM1MDYgLTAuMDA5LC0zLjQyOTE1IC0wLjEzMjQ3LC0zLjg4NyAtMS4zMzUzMiwtNC45NjQxMyAtMC41NzgzNiwtMC41MTc5IC0xLjQ4NzkxLC0wLjk2MjQ2IC0zLjQ2NDgsLTEuNjkzNDYgLTAuNzQ2MTYsLTAuMjc1OTIgLTIuODEwMjksLTEuMzM3MzMgLTMuNDQ5NDEsLTEuNzczNzYgLTEuMTA4ODksLTAuNzU3MjEgLTIuMjgwODgsLTEuNzU2ODEgLTIuMjgwODgsLTEuOTQ1MzkgMCwtMC4xMDAyMyAtMC4yNDg4MiwtMC43MTUzNSAtMC41NTI5MiwtMS4zNjY5NSAtMC40OTg4MSwtMS4wNjg3NyAtMC41NTE0NywtMS4zOTU0NSAtMC41MzgwMywtMy4zMzc4OCAwLjAxNjIsLTIuMzM5NjQgMC4xNzUyNCwtMi45NjczMyAxLjY5Njg3LC02LjY5NjE5IDEuMDY0MjYsLTIuNjA4MDMyIDEuMTUyNjIsLTMuMjQzNTgyIDAuNjE3NTIsLTQuNDQxNTcyIC0wLjQ0NzYyLC0xLjAwMjEzIC0yLjMyODY1LC0zLjE4NTggLTMuNjk1MDUsLTQuMjg5NTQgLTAuNDQzOTMsLTAuMzU4NiAtMS4yNTUxNCwtMC44MDY2NyAtMS44MDI2NywtMC45OTU3MiAtMS4xNzE5LC0wLjQwNDYxIC0yLjEwNzE4LC0wLjIyNzg0IC00LjIxNDE0LDAuNzk2NDkgLTIuNzA1MTYsMS4zMTUxNSAtNC4wODM4NSwxLjY4MjIxIC02LjMxODQ5LDEuNjgyMjEgLTEuNzk5ODcsMCAtMi4yMTI0OCwtMC4wNjgxIC0zLjE0NzY5LC0wLjUxOTc0IC0xLjE0NzkxLC0wLjU1NDMyIC0yLjQ1NjI2LC0xLjc5MjIzIC0zLjEzNTEzLC0yLjk2NjMzIC0wLjg4NTQzLC0xLjUzMTM2IC0yLjAzMjUyLC00LjA2NTQ2IC0yLjAzMjUyLC00LjQ5MDE3IDAsLTAuODg1MzQgLTEuNzY4MDcsLTMuMjE5Nzk2IC0yLjc1ODE2LC0zLjY0MTcxNiAtMS4wNDMwNywtMC40NDQ0OSAtMy42MTEwMiwtMC41NzI2IC01LjUxMzI1LC0wLjI3NTA0IC0xLjU5MzczLDAuMjQ5MyAtMS43MjkzNywwLjMxMjE0IC0yLjYwNjksMS4yMDc3NCAtMC45MjU5NSwwLjk0NTAyNiAtMS4wMjM4MywxLjE2ODU0NiAtMi4wMzAwNyw0LjYzNTg5NiAtMC42Mzk2LDIuMjAzOTQgLTIuNzQ5MjUsNC43MzY2MSAtNC42ODg2Nyw1LjYyODg0IC0wLjgzNDEzLDAuMzgzNzQgLTEuMzUzNywwLjQ2MDQ0IC0zLjExMjQ0LDAuNDU5NDYgLTIuMjk1MjIsLTAuMDAxIC0zLjc1MTY2LC0wLjM4MDc0IC02LjU3Mjc2LC0xLjcxMjQ4IC0wLjc1Mjk2LC0wLjM1NTQ1IC0xLjgwOTY5LC0wLjc2NDgyIC0yLjM0ODI4LC0wLjkwOTczIC0wLjg4MjMyLC0wLjIzNzM4IC0xLjA5MDY0LC0wLjIyMDk2IC0yLjEwNDQ3LDAuMTY1OTEgLTAuODg2NDksMC4zMzgyOCAtMS41MTYyLDAuODI1MTUgLTIuOTY4MTUsMi4yOTQ4OSAtMS45MDg0NCwxLjkzMTggLTIuNjk0NTcsMy4yMjQxOCAtMi42OTQ1Nyw0LjQyOTc3IDAsMC4zNTEyNiAwLjM2NzIsMS40NDA2IDAuODE2LDIuNDIwNzUyIDEuMzk3MTQsMy4wNTEyNiAxLjcwMzA0LDMuOTQzNDcgMi4wMzQwNyw1LjkzMjc0IDAuNDMwMSwyLjU4NDU2IC0wLjI1NDM0LDQuNjA2ODYgLTIuMTc5NjMsNi40NDAxMiAtMS4wMDA1OSwwLjk1Mjc2IC0zLjMzNzA4LDIuMzUwOCAtNC44OTI3NiwyLjkyNzU4IC0yLjUxNzQ5LDAuOTMzMzcgLTMuMDc1MzMsMS4yMTc5MSAtMy43NjMyNSwxLjkxOTUyIC0xLjA1OTcyNywxLjA4MDgxIC0xLjI2MzcxNywxLjgzMDU1IC0xLjI2MDI3Nyw0LjYzMjExIDAuMDA1LDQuMjI5ODggMC41Mjg3OCw1LjExNTAyIDMuNzcwNDk3LDYuMzc0MDkgNC40ODM5LDEuNzQxNTMgNi4yNzEsMy4wMDQzOCA3LjMxNzAxLDUuMTcwNTMgMC41NjYxMywxLjE3MjM4IDAuNjgyOTUsMS42NjIxIDAuNzQzNzQsMy4xMTc2MyAwLjA5ODYsMi4zNjA2OCAtMC4zMjA2Niw0LjA0OTI2IC0xLjgzOTMyLDcuNDA4MjggLTEuNTA4ODcsMy4zMzczNyAtMS4yNzM5LDQuNDQ3NTEgMS41NjUyNiw3LjM5NTI0IDIuODUzNDksMi45NjI2IDQuMDEzMTYsMy4yNjMyMSA3LjA2MTQ3LDEuODMwNDMgMy4zNjA5OCwtMS41Nzk3NSA0LjYxNjg1LC0xLjk0NzA2IDYuNjExNywtMS45MzM3NSAxLjM2MDEzLDAuMDA5IDEuNzk0OTYsMC4xMDM5NSAyLjgxNjAzLDAuNjE0NDYgMS45NjU4NSwwLjk4Mjg5IDMuMDc3MjksMS45MjE4NSAzLjk4Mzk4LDMuMzY1NzEgMS4yNjI2NSwyLjAxMDczIDEuMzM2MDEsMi4xMzQ0MyAxLjQ2MzA5LDIuNDY3MTUgMC4wNjQ2LDAuMTY5MTcgMC4xOTUyLDAuNDkyMTUgMC4yOTAxOCwwLjcxNzcyIDAuMDk1LDAuMjI1NTcgMC4zMTQzLDAuODU1NjMgMC40ODczNSwxLjQwMDEzIDAuMTczMDYsMC41NDQ1IDAuNDQxNTksMS4yMzY1OSAwLjU5Njc1LDEuNTM3OTcgMC40MDA5LDAuNzc4NzUgMS43MTYwNywxLjk5ODI5IDIuNDI2NCwyLjI0OTk4IDAuODU1OTYsMC4zMDMyOCA1LjkwMjIyLDAuMjg4MjkgNi41NTk3NiwtMC4wMTk1IHogbSAtNi45NjE4OSwtMjAuODcyMDcgYyAtMS45NDY2NCwtMC40MzU2NiAtMy4zNTExOCwtMC45NTExNyAtNS4yMjc2MywtMS45MTg3MSAtMi4zMzY5MiwtMS4yMDQ5NyAtNC41OTgyNywtMy4yNTQ5NyAtNi41Njk5NCwtNS45NTU5MSAtNC45OTc1NywtNi44NDYwMyAtNS4wMjQ2OCwtMTYuODExMjUgLTAuMDYzOCwtMjMuNDY0MTMgMi43Mzk4OCwtMy42NzQzOCA2LjEyNzczLC01Ljk0OTc1IDEwLjc1NTU2LC03LjIyMzcyIDEuODUxNzUsLTAuNTA5NzUgMi40NjU2OCwtMC41ODE2MiA0Ljk5NjM0LC0wLjU4NDgzIDMuNTM5OTYsLTAuMDA0IDUuNjczMTYsMC40OTk1NyA4Ljg2OTEzLDIuMDk1NzUgMS44OTE5NiwwLjk0NDkgMi4zNDM4NywxLjI4ODgzIDQuNDk3NjMsMy40MjI5OCAyLjQyNiwyLjQwMzkyIDMuMjQwODMsMy40ODY0NCA0LjIwNTI1LDUuNTg2NzkgMi42NjQ3LDUuODAzMjUgMi41ODA3OSwxMi4yODk3NiAtMC4yMzI1MSwxNy45NzM3NSAtMS40MDY4MiwyLjg0MjM0IC01LjE5OCw2LjYwMDI5IC04LjE2NDUsOC4wOTI5NCAtMy43Njk1LDEuODk2NyAtNS4wMjc2MSwyLjE5NTU5IC05LjE0NDc3LDIuMTcyNTMgLTEuNzE0MDYsLTAuMDEgLTMuNDc4MzksLTAuMDk4NCAtMy45MjA3MywtMC4xOTc0NCB6IgogICAgICAgaWQ9InBhdGgyIiAvPgogIDwvZz4KPC9zdmc+Cg==)]
[![Tests](https://github.com/shipt/opsml/actions/workflows/lint-unit-tests.yml/badge.svg?branch=main)](https://github.com/shipt/opsml/actions/workflows/lint-unit-tests.yml)
[![Examples](https://github.com/shipt/opsml/actions/workflows/example-tests.yml/badge.svg)](https://github.com/shipt/opsml/actions/workflows/example-tests.yml)
![Style](https://img.shields.io/badge/code%20style-black-000000.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Py-Versions](https://img.shields.io/pypi/pyversions/opsml.svg?color=%2334D058)](https://pypi.org/project/opsml)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://docs.pydantic.dev/latest/contributing/#badges)
[![gitleaks](https://img.shields.io/badge/protected%20by-gitleaks-purple)](https://github.com/zricethezav/gitleaks-action)


## What is it?

`OpsML` provides tooling that enables data science and engineering teams to better govern and manage their machine learning projects and artifacts.


## Features:
  - **Simple Design**: Standardized design that can easily be incorporated into existing projects.

  - **Cards**: Track, version and store a variety of ML artifacts via cards (data, models, runs, projects) and a SQL-based card registry system. Think `trading cards for machine learning`.

  - **Type Checking**: Strongly typed and type checking for data and model artifacts.

  - **Support**: Robust support for a variety of ML and data libraries.

  - **Automation**: Automated processes including onnx model conversion, metadata creation and production packaging.


## Installation:

### Poetry

```bash
poetry add opsml
```

### Pip

```bash
pip install opsml
```

Setup your local environment:

By default, `opsml` will log artifacts and experiments locally. To change this behavior and log to a remote server, you'll need to set the following environment variables:

```shell
export OPSML_TRACKING_URI=${YOUR_TRACKING_URI}
```

## Quickstart

If running the example below locally without a server, make sure to install the `server` extra:

```bash 
poetry add "opsml[server]"
```

```python
# imports
from sklearn.linear_model import LinearRegression
from opsml import (
    CardInfo,
    CardRegistries,
    DataCard,
    DataSplit,
    ModelCard,
    PandasData,
    SklearnModel,
)
from opsml.helpers.data import create_fake_data


info = CardInfo(name="linear-regression", team="opsml", user_email="user@email.com")
registries = CardRegistries()


#--------- Create DataCard ---------#

# create fake data
X, y = create_fake_data(n_samples=1000, task_type="regression")
X["target"] = y

# Create data interface
data_interface = PandasData(
    data=X,
    data_splits=[
        DataSplit(label="train", column_name="col_1", column_value=0.5, inequality=">="),
        DataSplit(label="test", column_name="col_1", column_value=0.5, inequality="<"),
    ],
    dependent_vars=["target"],
)

# Create and register datacard
datacard = DataCard(interface=data_interface, info=info)
registries.data.register_card(card=datacard)

#--------- Create ModelCard ---------#

# split data
data = datacard.split_data()

# fit model
reg = LinearRegression()
reg.fit(data.train.X.to_numpy(), data.train.y.to_numpy())

# create model interface
interface = SklearnModel(
    model=reg,
    sample_data=data.train.X.to_numpy(),
    task_type="regression",  # optional
)

# create modelcard
modelcard = ModelCard(
    interface=interface,
    info=info,
    to_onnx=True,  # lets convert onnx
    datacard_uid=datacard.uid,  # modelcards must be associated with a datacard
)
registries.model.register_card(card=modelcard)
```

## Table of Contents
- [Table of Contents](#table-of-contents)
- [Usage](#usage)
- [Advanced Installation Scenarios](#advanced-installation-scenarios)
- [Environment Variables](#environment-variables)
- [Supported Libraries](#supported-libraries)
- [Contributing](#contributing)

## Usage

Now that `opsml` is installed, you're ready to start using it!

It's time to point you to the official [Documentation Website](https://thorrester.github.io/opsml-ghpages/) for more information on how to use `opsml`


## Advanced Installation Scenarios

`Opsml` is designed to work with a variety of 3rd-party integrations depending on your use-case.

Types of extras that can be installed:

- **Postgres**: Installs postgres pyscopg2 dependency to be used with `Opsml`
  ```bash
  poetry add "opsml[postgres]"
  ```

- **Server**: Installs necessary packages for setting up a `Fastapi`-based `Opsml` server
  ```bash
  poetry add "opsml[server]"
  ```

- **GCP with mysql**: Installs mysql and gcsfs to be used with `Opsml`
  ```bash
  poetry add "opsml[gcs,mysql]"
  ```

- **GCP with mysql(cloud-sql)**: Installs mysql and cloud-sql gcp dependencies to be used with `Opsml`
  ```bash
  poetry add "opsml[gcp_mysql]"
  ```

- **GCP with postgres**: Installs postgres and gcsgs to be used with `Opsml`
  ```bash
  poetry add "opsml[gcs,postgres]"
  ```

- **GCP with postgres(cloud-sql)**: Installs postgres and cloud-sql gcp dependencies to be used with `Opsml`
  ```bash
  poetry add "opsml[gcp_postgres]"
  ```

- **AWS with postgres**: Installs postgres and s3fs dependencies to be used with `Opsml`
  ```bash
  poetry add "opsml[s3,postgres]"
  ```

- **AWS with mysql**: Installs mysql and s3fs dependencies to be used with `Opsml`
  ```bash
  poetry add "opsml[s3,mysql]"
  ```

## Environment Variables

The following environment variables are used to configure opsml. When using
opsml as a client (i.e., not running a server), the only variable that must be
set is `OPSML_TRACKING_URI`.

| Name                       | Description                                                                                                                     |
|----------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| APP_ENV                    | The environment to use. Supports `development`, `staging`, and `production`                                                      |
| GOOGLE_ACCOUNT_JSON_BASE64 | The base64 string of the the GCP service account to use.                                                                        |
| OPSML_MAX_OVERFLOW         | The SQL "max_overflow" size. Defaults to 5                                                                                      |
| OPSML_POOL_SIZE            | The SQL connection pool size. Defaults to 10.                                                                                   |
| OPSML_STORAGE_URI          | The location of storage to use. Supports a local file system, AWS, and GCS. Example: `gs://some-bucket`                         |
| OPSML_TRACKING_URI         | Used when logging artifacts to an opsml server (a.k.a., the server which "tracks" artifacts)                                    |
| OPSML_USERNAME             | An optional server username. If the server is setup with login enabled, all clients must use HTTP basic auth with this username |
| OPSML_PASSWORD             | An optional server password. If the server is setup with login enabled, all clients must use HTTP basic auth with this password |
| OPSML_RUN_ID               | If set, the run will be automatically loaded when creating new cards.                                                           |


# Supported Libraries

`Opsml` is designed to work with a variety of ML and data libraries. The following libraries are currently supported:

## Data Libraries

| Name          |  Opsml Implementation    |    Docs     |                                
|---------------|:-----------------------: |:-----------:|
| Pandas        | `PandasData`             | [link]()    |
| Polars        | `PolarsData`             | [link]()    |                                                            
| Torch         | `TorchData`              | [link]()    |                                                                     
| Arrow         | `ArrowData`              | [link]()    |                                                                              
| Numpy         | `NumpyData`              | [link]()    |                        
| Sql           | `SqlData`                | [link]()    |                     
| Text          | `TextDataset`            | [link]()    | 
| Image         | `ImageDataset`           | [link]()    | 

## Model Libraries

| Name          |  Opsml Implementation      |    Docs     |    Example                                          |                                
|-----------------|:-----------------------: |:-----------:|:--------------------------------------------------: |
| Sklearn         | `SklearnModel`           | [link]()    | [link](examples/sklearn/basic.py)                   |
| LightGBM        | `LightGBMModel`          | [link]()    | [link](examples/boosters/lightgbm_boost.py)         |                                                           
| XGBoost         | `XGBoostModel`           | [link]()    | [link](examples/boosters/xgboost_sklearn.py)        |                                                                     
| CatBoost        | `CatBoostModel`          | [link]()    | [link](examples/boosters/catboost_example.py)       |                                                                              
| Torch           | `TorchModel`             | [link]()    | [link](examples/torch/torch_example.py)             |                        
| Torch Lightning | `LightningModel`         | [link]()    | [link](examples/torch/torch_lightning_example.py)   |                     
| TensorFlow      | `TensorFlowModel`        | [link]()    | [link]()                                            | 
| HuggingFace     | `HuggingFaceModel`       | [link]()    | [link](examples/huggingface/hf_example.py)          | 


## Contributing
If you'd like to contribute, be sure to check out our [contributing guide](./CONTRIBUTING.md)! If you'd like to work on any outstanding items, check out the `roadmap` section in the docs and get started :smiley:

Thanks goes to these phenomenal [projects and people](./ATTRIBUTIONS.md) and people for creating a great foundation to build from!

<a href="https://github.com/shipt/opsml/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=shipt/opsml" />
</a>

