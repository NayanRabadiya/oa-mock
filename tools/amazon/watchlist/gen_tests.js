// Builds the watchlist tests: expected output comes from the fixed repo; the buggy starter must fail them.
const fs=require('fs'), path=require('path'), run=require('./runjs.js');
const P=f=>path.join(__dirname,f);
const pre=fs.readFileSync(P('prelude.js'),'utf8'), post=fs.readFileSync(P('post.js'),'utf8');
const M=i=>"65f0a1b2c3d4e5f6"+String(i).padStart(8,"0");
const add=(t,u,id)=>`${t} ${u} POST /api/watchlist/add ${id===undefined?"{}":JSON.stringify({movieId:id})}`;
const rem=(t,u,id)=>`${t} ${u} POST /api/watchlist/remove ${id===undefined?"{}":JSON.stringify({movieId:id})}`;
const get=(t,u)=>`${t} ${u} GET /api/watchlist/`;
const chk=(t,u,id)=>`${t} ${u} GET /api/watchlist/check/${id}`;
const tests={
 samples:[
  {name:"Added movie shows on the watchlist", lines:[add(0,"sam",M(2)),get(1,"sam")], ex:"Adding Interstellar returns 201, and the watchlist then lists it. The buggy repo returns 500 for the list."},
  {name:"Watchlist status is a boolean", lines:[chk(0,"sam",M(2)),add(1,"sam",M(2)),chk(2,"sam",M(2)),chk(3,"sam","abc")], ex:"check must return true or false, not the array that find() gives back."},
 ],
 hidden:[
  {name:"Add several movies and view them, per user", lines:[add(0,"sam",M(1)),add(1,"sam",M(3)),add(2,"alex",M(4)),get(3,"sam"),get(4,"alex"),add(5,"sam",M(6)),get(6,"sam")]},
  {name:"Remove a movie from the watchlist", lines:[add(0,"sam",M(1)),add(1,"sam",M(2)),rem(2,"sam",M(1)),get(3,"sam"),chk(4,"sam",M(1)),rem(5,"sam",M(1)),chk(6,"sam",M(2))]},
  {name:"Duplicates and removing a missing movie", lines:[add(0,"sam",M(5)),add(1,"sam",M(5)),get(2,"sam"),rem(3,"sam",M(4)),rem(4,"sam",M(5)),add(5,"sam",M(5)),get(6,"sam"),add(7,"alex",M(5))]},
  {name:"Validation and auth errors", lines:[add(0,"sam"),add(1,"sam","123"),add(2,"sam",M(255)),rem(3,"sam"),rem(4,"sam","not-an-id"),chk(5,"sam","xyz"),get(6,"-"),add(7,"-",M(1)),get(8,"sam")]},
  {name:"Rate limit: 10 add/remove operations per 2 minutes, combined", lines:[...[1,2,3,4,5].flatMap((m,i)=>[add(i*2,"sam",M(m)),rem(i*2+1,"sam",M(m))]),add(10,"sam",M(6)),get(11,"sam"),add(12,"alex",M(6)),rem(13,"sam",M(6)),add(125,"sam",M(6)),get(126,"sam")]},
  {name:"Rate limit window slides", lines:[...Array.from({length:10},(_,i)=>add(i,"sam",i%2?M(1):M(2))),add(60,"sam",M(3)),rem(119,"sam",M(1)),rem(120,"sam",M(1)),add(121,"sam",M(3)),add(122,"sam",M(4)),get(123,"sam"),chk(124,"sam",M(3))]},
  {name:"Failed requests count toward the limit", lines:[...Array.from({length:10},(_,i)=>add(i,"alex","bad"+i)),add(10,"alex",M(2)),get(11,"alex"),add(10,"sam",M(2)),add(131,"alex",M(2)),get(132,"alex")]},
  {name:"Long session", lines:[add(0,"sam",M(1)),add(5,"sam",M(2)),add(10,"sam",M(3)),rem(15,"sam",M(2)),add(20,"sam",M(2)),get(25,"sam"),chk(26,"sam",M(2)),rem(30,"sam",M(9)),add(35,"sam",M(4)),add(40,"sam",M(5)),add(45,"sam",M(6)),rem(50,"sam",M(1)),add(55,"sam",M(1)),get(56,"sam"),rem(57,"sam",M(4)),get(200,"sam"),rem(201,"sam",M(4)),add(202,"sam",M(4)),get(203,"sam")]},
 ]
};
(async()=>{
 const fixed=fs.readFileSync(P('fixed.js'),'utf8'), starter=fs.readFileSync(P('starter.js'),'utf8');
 const strip=s=>s.split("\n").filter(l=>!l.startsWith("[log]")).join("\n").trim();
 const res={samples:[],hidden:[]};
 for (const k of ["samples","hidden"]) for (const t of tests[k]) {
   const inp="# "+t.name+"\n"+t.lines.join("\n")+"\n";
   const r=await run(pre+"\n"+fixed+"\n"+post, inp);
   if (r.err) throw new Error(r.err);
   const o={in:inp, out:strip(r.out)}; if(t.ex) o.ex=t.ex; res[k].push(o);
   const b=await run(pre+"\n"+starter+"\n"+post, inp);
   console.log("==",t.name,"| starter passes:",strip(b.out)===o.out, b.err?("ERR "+b.err):"");
 }
 fs.writeFileSync(P('../build/watchlist_tests.json'),JSON.stringify(res));
})();
