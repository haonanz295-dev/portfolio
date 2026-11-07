/* Additive UI keeps the v0.2 layout and one shared settings menu. */
(() => {
 const emotes=document.querySelector('#emotes');
 for(const [id,title,description] of [['raise','抬起双手','试着让伙伴看见你'],['spin','转个圈圈','邀请它用绕游回应'],['bubbles','送出气泡','看看它会怎么回应'],['bow','轻轻点头','不用说话也能问候'],['stretch','舒展一下','让水托住身体']]){const b=document.createElement('button');b.dataset.action=id;b.append(document.createTextNode(title));const small=document.createElement('small');small.textContent=description;b.append(small);emotes.append(b)}
 const grid=document.querySelector('#pause .grid');for(const [id,title] of [['profile-manage','我的探索档案'],['moment-open','回看一个瞬间']]){const b=document.createElement('button');b.id=id;b.textContent=title;grid.append(b)}
})();
