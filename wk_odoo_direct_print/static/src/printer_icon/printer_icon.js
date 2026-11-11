/** @odoo-module **/

import { Component, useState, onWillStart, useRef, useEffect } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

const LIMIT = 20;

export class WkPrintJobsMenu extends Component {
    static template = "wk_odoo_direct_print.WkPrintJobsMenu";
    static props = {};

    setup() {
        this.orm    = useService("orm");
        this.action = useService("action");
        this.root   = useRef("root");

        this.state = useState({
            open:       false,
            jobs:       [],
            offset:     0,
            hasMore:    false,
            loading:    false,
            badgeCount: 0,
        });

        onWillStart(() => Promise.all([this._load(), this._loadBadge()]));

        useEffect(() => {
            const handler = (e) => {
                if (this.state.open && !this.root.el?.contains(e.target)) {
                    this.state.open = false;
                }
            };
            document.addEventListener("click", handler, true);
            return () => document.removeEventListener("click", handler, true);
        });
    }

    async _load(offset = 0) {
        this.state.loading = true;

        const records = await this.orm.searchRead(
            "print.jobs",
            [],
            ["name", "state", "printer_id", "msg", "write_date",
                "print_job_for", "model_ref", "rec_ref"],
            { order: "write_date desc", limit: LIMIT + 1, offset }
        );

        const hasMore = records.length > LIMIT;
        const data    = hasMore ? records.slice(0, LIMIT) : records;

        if (offset === 0) {
            this.state.jobs = data;
        } else {
            this.state.jobs = [...this.state.jobs, ...data];
        }

        this.state.offset  = offset;
        this.state.hasMore = hasMore;
        this.state.loading = false;
    }

    async _loadBadge() {
        this.state.badgeCount = await this.orm.searchCount(
            "print.jobs",
            [["state", "in", ["Queue", "Failed"]]]
        );
    }

    async toggle() {
        if (!this.state.open) {
            await Promise.all([this._load(), this._loadBadge()]);
        }
        this.state.open = !this.state.open;
    }

    async loadMore() {
        await this._load(this.state.offset + LIMIT);
    }

    async retryJob(jobId, ev) {
        ev.stopPropagation();
        await this.orm.call("print.jobs", "retry_print", [[jobId]]);
        await Promise.all([this._load(), this._loadBadge()]);
    }

    openAll() {
        this.state.open = false;
        this.action.doAction({
            type:      "ir.actions.act_window",
            name:      "Print Jobs",
            res_model: "print.jobs",
            view_mode: "list,form",
            views:     [[false, "list"], [false, "form"]],
            target:    "current",
        });
    }

    openJob(jobId) {
        this.state.open = false;
        this.action.doAction({
            type:      "ir.actions.act_window",
            name:      "Print Job",
            res_model: "print.jobs",
            res_id:    jobId,
            view_mode: "form",
            views:     [[false, "form"]],
            target:    "current",
        });
    }

    formatTime(dateStr) {
        if (!dateStr) return "";
        const date = new Date(dateStr);
        const now  = new Date();
        const diff = Math.floor((now - date) / 1000);

        if (diff < 60)     return "Just now";
        if (diff < 3600)   return `${Math.floor(diff / 60)} min ago`;
        if (diff < 86400)  return `${Math.floor(diff / 3600)} hr ago`;
        if (diff < 172800) return "Yesterday";
        return date.toLocaleDateString("en-GB", { day: "2-digit", month: "short" });
    }
}

registry.category("systray").add("wk.PrintJobsMenu", {
    Component: WkPrintJobsMenu,
    sequence:  99,
});
