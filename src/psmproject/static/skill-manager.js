/** Class used to store variables and methods for managing skills on edit and create templates. */
export default class SkillManager {
    /**
     * Create skill manager, init internal variables and link variables with document elements
     */
    constructor() {
        this.skills = JSON.parse(document.getElementById('skills').textContent);
        this.skillSelIDPrefix = JSON.parse(document.getElementById('skillIDPrefix').textContent);
        this.skillPosIDPrefix = "pos-skill-";
        this.filterInput = document.getElementById('filter-skills');
        this.selectedSkillList = document.getElementById("selected-skills-list");
        this.skillList = document.getElementById("pos-skills-list");
        this.initEventListeners();
    }

    /**
     * Prepare and append document element for single skill input button that already exists in the parent object
     * (Task) and is part of the form. Creates html tags, adds classes and contents
     */
    renderSkillForm(skill, idPrefix, onClick, parent) {
        const skillButton = document.createElement("button");
        skillButton.id = idPrefix + skill.id;
        skillButton.innerHTML = skill.skill;
        skillButton.onclick = onClick;
        skillButton.classList.add("btn", "btn-primary", "btn-sm", "ms-1");

        const skillInput = document.createElement("input");
        skillInput.name = idPrefix + skill.id;
        skillInput.type = "hidden";
        skillInput.value = skill.skill;

        skillButton.appendChild(skillInput);
        parent.appendChild(skillButton);
    }

    /**
     * Prepare and append document element for single skill on selection list. Creates html tags, adds classes
     * and contents
     */
    renderSkill(skill, idPrefix, onClick, parent) {
        const skillSpan = document.createElement("span");
        skillSpan.id = idPrefix + skill.id;
        skillSpan.classList.add("badge", "text-bg-primary", "ms-1");
        skillSpan.innerHTML = skill.skill;
        skillSpan.onclick = onClick;
        parent.appendChild(skillSpan);
    }

    /**
     * Remove skill from parent element
     */
    removeSkill(skill, idPrefix, parent) {
        const skill_el = document.getElementById(idPrefix + skill.id);
        parent.removeChild(skill_el);
    }

    /**
     * Select skill and add it to the parent object (Task). Method removes it also from selection list.
     */
    selectSkill(skill) {
        this.renderSkillForm(skill, this.skillSelIDPrefix, () => this.deselectSkill(skill), this.selectedSkillList);
        this.removeSkill(skill, this.skillPosIDPrefix, this.skillList);
        const index = this.skills.findIndex(item => item.id === skill.id);
        this.skills.splice(index, 1);
    }

    /**
     * Remove skill from the parent object (Task). Method also updates selection list after removal from form.
     */
    deselectSkill(skill) {
        this.removeSkill(skill, this.skillSelIDPrefix, this.selectedSkillList);
        this.skills.push(skill);
        this.displayList(this.skills, this.filterInput.value);
    }

    /**
     * Display list of all skills matching filter criteria.
     */
    displayList(skills, filter) {
        this.skillList.innerHTML = '';
        if (filter.length > 0) {
            const results = skills.filter(obj => {
                return obj.skill.toLowerCase().includes(filter.toLowerCase());
            });

            for (const skill of results) {
                this.renderSkill(skill, this.skillPosIDPrefix, () => this.selectSkill(skill), this.skillList);
            }
        }
    }

    /**
     * Add onClick action to all skills existing on form. They are generate by the Django template without actions.
     */
    addOnClickToExistingSkills(parent) {
        const buttons_el = parent.getElementsByTagName("button");
        const buttons_el_arr = [...buttons_el];
        for (const button of buttons_el_arr) {
            const input = button.getElementsByTagName("input")[0];
            const skill_obj = { "id": button.id.replace(this.skillSelIDPrefix, ""), "skill": input.value }
            button.onclick = () => this.deselectSkill(skill_obj);
        }
    }

    /**
     * Init event listeners for document elements
     */
    initEventListeners() {
        this.addOnClickToExistingSkills(this.selectedSkillList);
        this.filterInput.addEventListener('input', (e) => {
            this.displayList(this.skills, e.target.value);
        });
    }
}
