import{d as t,c as e,o as a,w as s,a as i,t as n,r as o,b as l,F as c,e as d,f as r,g as u,B as m,A as h,E as p,h as g,l as y,i as v,j as _,k as f,m as k,n as w,p as C,q as b,s as S}from"./vendor.37a68ca1.js";!function(t=".",e="__import__"){try{self[e]=new Function("u","return import(u)")}catch(a){const s=new URL(t,location),i=t=>{URL.revokeObjectURL(t.src),t.remove()};self[e]=t=>new Promise(((a,n)=>{const o=new URL(t,s);if(self[e].moduleMap[o])return a(self[e].moduleMap[o]);const l=new Blob([`import * as m from '${o}';`,`${e}.moduleMap['${o}']=m;`],{type:"text/javascript"}),c=Object.assign(document.createElement("script"),{type:"module",src:URL.createObjectURL(l),onerror(){n(new Error(`Failed to import: ${t}`)),i(c)},onload(){a(self[e].moduleMap[o]),i(c)}});document.head.appendChild(c)})),self[e].moduleMap={}}}("assets/");const $=t({props:{data:{type:Object,default:()=>({cmd:"",text:""})}}}),x=i("a",null,"HomeAssistant",-1);$.render=function(t,l,c,d,r,u){const m=o("a-avatar"),h=o("a-comment");return a(),e(h,null,{author:s((()=>[x])),avatar:s((()=>[i(m,{src:"https://www.home-assistant.io/images/home-assistant-logo.svg",alt:"HomeAssistant"})])),content:s((()=>[i("p",null,n(t.data.text),1)])),_:1})};var M=t({props:{data:Object},inject:["callService"],methods:{showClick(t){const{entity_id:e}=this.data;e?(this.callService("media_player.play_media",{media_content_type:"video",media_content_id:t.value,entity_id:e}),this.$message.success(`正在播放${t.name}`)):this.$message.error("请先设置播放器")}}});const O=l(),A=O(((t,s,i,l,u,m)=>{const h=o("a-card-grid"),p=o("a-card");return a(),e(p,{title:t.data.text,size:"small"},{default:O((()=>[(a(!0),e(c,null,d(t.data.list,((s,i)=>(a(),e(h,{size:"small",style:{width:"25%","text-align":"center"},key:i,onClick:e=>t.showClick(s)},{default:O((()=>[r(n(s.name),1)])),_:2},1032,["onClick"])))),128))])),_:1},8,["title"])}));M.render=A,M.__scopeId="data-v-5aeed5f4";const V={props:{data:{type:Object,default:()=>({domain:"",value:"",entity_id:"",isAction:!1})}},data:()=>({}),inject:["callService"],methods:{toggleClick(){const{value:t,domain:e,entity_id:a}=this.data;this.callService(`${e}.turn_${"on"===t?"off":"on"}`,{entity_id:a}),this.$message.success("切换成功"),this.$emit("toggle")},triggerClick(){const{domain:t,entity_id:e}=this.data;"script"===t?this.callService(e):"automation"===t&&this.callService("automation.trigger",{entity_id:e}),this.$message.success("触发成功"),this.$emit("trigger")},sourceListChange(t){const{domain:e,entity_id:a}=this.data;this.callService("media_player.select_source",{entity_id:a,source:t}),this.$message.success(`选择【${t}】`)},format_source_list:t=>t.map((t=>({value:t,label:t})))}},j=r("触发"),L={key:3};V.render=function(t,i,l,c,d,r){const u=o("a-switch"),m=o("a-button"),h=o("a-select");return l.data.isAction&&["input_boolean","light","switch","fan","automation","climate"].includes(l.data.domain)?(a(),e(u,{key:0,checked:"on"===l.data.value,onClick:r.toggleClick},null,8,["checked","onClick"])):l.data.isAction&&["script","scene","automation"].includes(l.data.domain)?(a(),e(m,{key:1,type:"link",onClick:r.triggerClick},{default:s((()=>[j])),_:1},8,["onClick"])):"source_list"===l.data.name?(a(),e(h,{key:2,style:{width:"200px"},options:r.format_source_list(l.data.value),onChange:r.sourceListChange},null,8,["options","onChange"])):(a(),e("span",L,n(l.data.value),1))};var U=t({components:{ActionButton:V},props:{data:{type:Object,default:()=>({cmd:"",text:"",list:[]})},hass:{},load:Function},data:()=>({list:[],entity:null}),inject:["callService"],async mounted(){const t=this.data.list;if(this.list=await this.load({entity_list:t}),1===t.length){const e=t[0].split(".")[0];"media_player"===e&&(this.entity={domain:e,entity_id:t[0],volume_level:100*this.list.find((t=>"volume_level"===t.name)).value})}},methods:{toggleClick(t){t.value="on"===t.value?"off":"on"},musicEvent({service:t}){const{entity_id:e,volume_level:a}=this.entity;let s={entity_id:e};"volume_set"===t&&(s.volume_level=a/100),this.callService(`media_player.${t}`,s),this.$message.success("操作成功")}}});const E={key:0,style:{"text-align":"center"}},T=r("上一曲"),P=r("播放/暂停"),R=r("下一曲");U.render=function(t,l,m,h,p,g){const y=o("a-button"),v=o("a-space"),_=o("a-slider"),f=o("ActionButton"),k=o("a-list-item"),w=o("a-list");return a(),e(c,null,[t.entity?(a(),e(c,{key:0},["media_player"===t.entity.domain?(a(),e("div",E,[i(v,null,{default:s((()=>[i(y,{type:"primary",onClick:l[1]||(l[1]=e=>t.musicEvent({service:"media_previous_track"}))},{default:s((()=>[T])),_:1}),i(y,{type:"primary",onClick:l[2]||(l[2]=e=>t.musicEvent({service:"media_play_pause"}))},{default:s((()=>[P])),_:1}),i(y,{type:"primary",onClick:l[3]||(l[3]=e=>t.musicEvent({service:"media_next_track"}))},{default:s((()=>[R])),_:1})])),_:1}),i(_,{value:t.entity.volume_level,"onUpdate:value":l[4]||(l[4]=e=>t.entity.volume_level=e),onAfterChange:l[5]||(l[5]=e=>t.musicEvent({service:"volume_set"}))},null,8,["value"])])):u("",!0)],64)):u("",!0),i(w,{bordered:""},{default:s((()=>[(a(!0),e(c,null,d(t.list,((o,l)=>(a(),e(k,{key:l},{actions:s((()=>[i(f,{data:o,onToggle:e=>t.toggleClick(o)},null,8,["data","onToggle"])])),default:s((()=>[r(n(o.name)+" ",1)])),_:2},1024)))),128))])),_:1})],64)};const B={},z={style:{"text-align":"center",padding:"50px"}};B.render=function(t,s){const n=o("a-spin");return a(),e("div",z,[i(n,{size:"large"})])};var F=t({components:{BarsOutlined:m,AudioOutlined:h,EditOutlined:p,CardMessage:$,CardVideo:M,CardState:U,CardLoading:B},setup:()=>({hass:null,list:g([]),isVoice:g(!1)}),data(){return{msg:"",loading:!1,throttle:y.throttle((()=>{this.sendMsg(this.msg)}),2e3,{leading:!1,trailing:!0})}},watch:{msg(t){t&&this.isVoice&&this.throttle()}},provide(){return{callService:this.callService}},created(){this.connect()},methods:{async connect(){let t;try{t=await v({loadTokens(){try{return JSON.parse(localStorage.hassTokens)}catch(t){}},saveTokens:t=>{localStorage.hassTokens=JSON.stringify(t)}})}catch(a){if(a!==_)return void alert(`Unknown error: ${a}`);{const e=prompt("请输入要连接的HomeAssistant地址?",location.origin);t=await v({hassUrl:e})}}const e=await f({auth:t});location.search.includes("auth_callback=1")&&history.replaceState(null,"",location.pathname),this.hass=e,k(e).then((t=>{console.log("Logged in as",t),e.sendMessagePromise({type:"get_states"}).then((e=>{let a=e.find((t=>"conversation.voice"===t.entity_id)),s=new URLSearchParams(location.search),i=a.attributes.version;s.get("ver")!=i?location.search=`?ver=${i}`:this.list.push({name:"CardMessage",cmd:"HomeAssistant服务连接成功",data:{text:`【${t.name}】你好，欢迎使用语音小助手，当前版本${i}`}})}))}))},async callService(t,e={}){let a=t.split(".");const s=await this.hass.sendMessagePromise({type:"call_service",domain:a[0],service:a[1],service_data:e});return console.log(s),s},async loadData({entity_list:t}){await this.sleep(1);const e=(await this.hass.sendMessagePromise({type:"get_states"})).filter((e=>t.includes(e.entity_id))).map((t=>(t.domain=t.entity_id.split(".")[0],t)));let a=[];if(1===e.length){const{attributes:t,state:s,domain:i,entity_id:n}=e[0];a=Object.keys(t).map((e=>({domain:i,entity_id:n,name:e,value:t[e]}))),a.unshift({domain:i,entity_id:n,name:t.friendly_name,value:s,isAction:!0})}else a=e.map((t=>({domain:t.domain,entity_id:t.entity_id,name:t.attributes.friendly_name,value:t.state,isAction:!0})));return a},scrollIntoView(){setTimeout((()=>{const t=document.querySelector("#app .ant-card:nth-last-child(2)");t&&t.scrollIntoView({behavior:"smooth"})}),500)},sendMsgKeydown(t){const{msg:e,isVoice:a}=this;e&&!a&&this.sendMsg(e)},sleep:async t=>new Promise((e=>{setTimeout(e,1e3*t)})),sendMsg(t){this.msg="";const e={name:"CardLoading",cmd:t,data:{text:"",list:[]}};this.list.push(e),this.loading=!0,this.hass.sendMessagePromise({conversation_id:`${Math.random().toString(16).substr(2,10)}${Math.random().toString(16).substr(2,10)}`,text:t,type:"conversation/process"}).then((({speech:t})=>{e.data.text=t.plain.speech;const a=t.plain.extra_data;a?("video"===a.type?(e.name="CardVideo",e.data.entity_id=a.entity_id):e.name="CardState",e.data.list=a.data):e.name="CardMessage",this.list[this.list.length-1]=JSON.parse(JSON.stringify(e))})).finally((()=>{this.loading=!1})),this.scrollIntoView()},toggleVoiceClick(){this.isVoice=!this.isVoice}}});const H={style:{position:"fixed",bottom:"0",left:"0",width:"100%",padding:"10px",background:"white"}};F.render=function(t,n,l,r,u,m){const h=o("a-card"),p=o("BarsOutlined"),g=o("AudioOutlined"),y=o("EditOutlined"),v=o("a-tooltip"),_=o("a-input");return a(),e(c,null,[(a(!0),e(c,null,d(t.list,((i,n)=>(a(),e(h,{size:"small",key:n,title:i.cmd},{default:s((()=>[(a(),e(C(i.name),{data:i.data,hass:t.hass,load:t.loadData},null,8,["data","hass","load"]))])),_:2},1032,["title"])))),128)),i("div",H,[i(_,{placeholder:"请输入文字命令",value:t.msg,"onUpdate:value":n[2]||(n[2]=e=>t.msg=e),valueModifiers:{trim:!0},onKeydown:w(t.sendMsgKeydown,["enter"]),disabled:t.loading},{prefix:s((()=>[i(p,{type:"user"})])),suffix:s((()=>[i(v,{title:t.isVoice?"自动发送":"手动发送"},{default:s((()=>[i("span",{onClick:n[1]||(n[1]=(...e)=>t.toggleVoiceClick&&t.toggleVoiceClick(...e))},[t.isVoice?(a(),e(g,{key:0,style:{color:"rgba(0, 0, 0, 0.45)"}})):(a(),e(y,{key:1,style:{color:"rgba(0, 0, 0, 0.45)"}}))])])),_:1},8,["title"])])),_:1},8,["value","onKeydown","disabled"])])],64)};b(F).use(S).mount("#app");
