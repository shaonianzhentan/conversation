import{d as t,c as e,r as a,o as s,w as n,a as o,t as l,b as r,e as i,U as c,I as d,g as u,F as h,f as m,h as p,i as f,j as g,A as w,k as _,E as y,l as v}from"./vendor.8537f8c2.js";!function(t=".",e="__import__"){try{self[e]=new Function("u","return import(u)")}catch(a){const s=new URL(t,location),n=t=>{URL.revokeObjectURL(t.src),t.remove()};self[e]=t=>new Promise(((a,o)=>{const l=new URL(t,s);if(self[e].moduleMap[l])return a(self[e].moduleMap[l]);const r=new Blob([`import * as m from '${l}';`,`${e}.moduleMap['${l}']=m;`],{type:"text/javascript"}),i=Object.assign(document.createElement("script"),{type:"module",src:URL.createObjectURL(r),onerror(){o(new Error(`Failed to import: ${t}`)),n(i)},onload(){a(self[e].moduleMap[l]),n(i)}});document.head.appendChild(i)})),self[e].moduleMap={}}}("assets/");const x=t({props:{data:{type:Object,default:()=>({cmd:"",text:""})}}}),b=o("a",null,"HomeAssistant",-1);x.render=function(t,r,i,c,d,u){const h=a("a-avatar"),m=a("a-comment"),p=a("a-card");return s(),e(p,{size:"small",title:t.data.cmd},{default:n((()=>[o(m,null,{author:n((()=>[b])),avatar:n((()=>[o(h,{src:"https://www.home-assistant.io/images/home-assistant-logo.svg",alt:"HomeAssistant"})])),content:n((()=>[o("p",null,l(t.data.text),1)])),_:1})])),_:1},8,["title"])};var k=t({props:{data:Object}});const M=r("第一集"),U=r("第二集"),S=r("第一集"),O=r("第一集"),$=r("第一集"),j=r("第一集"),L=r("第一集"),C=r("第一集");k.render=function(t,l,r,i,c,d){const u=a("a-card-grid"),h=a("a-card");return s(),e(h,{title:"我想看司藤",size:"small"},{default:n((()=>[o(h,{title:"获取所有状态值"},{default:n((()=>[o(u,{style:{width:"25%","text-align":"center"}},{default:n((()=>[M])),_:1}),o(u,{style:{width:"25%","text-align":"center"}},{default:n((()=>[U])),_:1}),o(u,{style:{width:"25%","text-align":"center"}},{default:n((()=>[S])),_:1}),o(u,{style:{width:"25%","text-align":"center"}},{default:n((()=>[O])),_:1}),o(u,{style:{width:"25%","text-align":"center"}},{default:n((()=>[$])),_:1}),o(u,{style:{width:"25%","text-align":"center"}},{default:n((()=>[j])),_:1}),o(u,{style:{width:"25%","text-align":"center"}},{default:n((()=>[L])),_:1}),o(u,{style:{width:"25%","text-align":"center"}},{default:n((()=>[C])),_:1})])),_:1})])),_:1})};var R=t({props:{data:{}},setup:()=>({checked:i(!1)})});const A=r("测试"),P=r("测试 "),E=r(" 10 "),H=r("测试 ");R.render=function(t,l,r,i,c,d){const u=a("a-list-item"),h=a("a-switch"),m=a("a-list"),p=a("a-card");return s(),e(p,{title:"我想看司藤"},{default:n((()=>[o(m,{bordered:""},{default:n((()=>[o(u,null,{default:n((()=>[A])),_:1}),o(u,null,{actions:n((()=>[E])),default:n((()=>[P])),_:1}),o(u,null,{actions:n((()=>[o(h,{checked:t.checked,"onUpdate:checked":l[1]||(l[1]=e=>t.checked=e)},null,8,["checked"])])),default:n((()=>[H])),_:1})])),_:1})])),_:1})};var T=t({components:{UserOutlined:c,InfoCircleOutlined:d,CardMessage:x,CardVideo:k,CardState:R},setup:()=>{let t=i("");return{list:i([]),msg:t}},created(){this.initData()},methods:{initData(){const t=this.hass;u(t).then((e=>{console.log("Logged in as",e),t.sendMessagePromise({type:"get_states"}).then((t=>{let a=t.find((t=>"conversation.voice"===t.entity_id)),s=new URLSearchParams(location.search),n=a.attributes.version;s.get("ver")!=n?location.search=`?ver=${n}`:this.list.push({name:"CardMessage",data:{cmd:"HomeAssistant服务连接成功",text:`【${e.name}】你好，欢迎使用语音小助手`}})}))}))},sendMsg(){const{msg:t,list:e}=this;this.msg="",this.hass.sendMessagePromise({conversation_id:`${Math.random().toString(16).substr(2,10)}${Math.random().toString(16).substr(2,10)}`,text:t,type:"conversation/process"}).then((({speech:a})=>{const s={cmd:String(t),text:a.plain.speech};e.push({name:"CardMessage",data:s})}))}}});const F={style:{position:"fixed",bottom:"0",left:"0",width:"100%",padding:"10px",background:"white"}};T.render=function(t,l,r,i,c,d){const u=a("user-outlined"),g=a("info-circle-outlined"),w=a("a-tooltip"),_=a("a-input");return s(),e(h,null,[(s(!0),e(h,null,m(t.list,((t,a)=>(s(),e(f(t.name),{key:a,data:t.data},null,8,["data"])))),128)),o("div",F,[o(_,{placeholder:"请输入文字命令",value:t.msg,"onUpdate:value":l[1]||(l[1]=e=>t.msg=e),onKeydown:p(t.sendMsg,["enter"])},{prefix:n((()=>[o(u,{type:"user"})])),suffix:n((()=>[o(w,{title:"Extra information"},{default:n((()=>[o(g,{style:{color:"rgba(0, 0, 0, 0.45)"}})])),_:1})])),_:1},8,["value","onKeydown"])])],64)};const z=g(T);!async function(){let t;try{t=await _({loadTokens(){try{return JSON.parse(localStorage.hassTokens)}catch(t){}},saveTokens:t=>{localStorage.hassTokens=JSON.stringify(t)}})}catch(a){if(a!==y)return void alert(`Unknown error: ${a}`);{const e=prompt("请输入要连接的HomeAssistant地址?","http://localhost:8123");t=await _({hassUrl:e})}}const e=await v({auth:t});location.search.includes("auth_callback=1")&&history.replaceState(null,"",location.pathname),z.config.globalProperties.hass=e}(),z.use(w).mount("#app");