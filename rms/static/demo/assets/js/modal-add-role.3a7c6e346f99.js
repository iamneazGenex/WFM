"use strict";document.addEventListener("DOMContentLoaded",(function(e){!function(){FormValidation.formValidation(document.getElementById("addRoleForm"),{fields:{modalRoleName:{validators:{notEmpty:{message:"Please enter role name"}}}},plugins:{trigger:new FormValidation.plugins.Trigger,bootstrap5:new FormValidation.plugins.Bootstrap5({eleValidClass:"",rowSelector:".col-12"}),submitButton:new FormValidation.plugins.SubmitButton,autoFocus:new FormValidation.plugins.AutoFocus}});const e=document.querySelector("#selectAll"),t=document.querySelectorAll('[type="checkbox"]');e.addEventListener("change",(e=>{t.forEach((t=>{t.checked=e.target.checked}))}))}()}));
