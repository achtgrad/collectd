/**
 * collectd - src/plugin.h
 * Copyright (C) 2005  Florian octo Forster
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
 *
 * Authors:
 *   Florian octo Forster <octo at verplant.org>
 **/

#ifndef PLUGIN_H
#define PLUGIN_H

/*
 * NAME
 *  plugin_set_dir
 *
 * DESCRIPTION
 *  Sets the current `plugindir'
 *
 * ARGUMENTS
 *  `dir'       Path to the plugin directory
 *
 * NOTES
 *  If `dir' is NULL the compiled in default `PLUGINDIR' is used.
 */
void plugin_set_dir (const char *dir);

/*
 * NAME
 *  plugin_count
 *
 * DESCRIPTION
 *  trivial
 *
 * RETURN VALUE
 *  The number of currently loaded plugins
 */
int plugin_count (void);

/*
 * NAME
 *  plugin_exists
 *
 * DESCRIPTION
 *  trivial
 *
 * ARGUMENTS
 *  `type'      Name of the plugin.
 *
 * RETURN VALUE
 *  Returns non-zero if a plugin with the name $type is found and zero
 *  otherwise.
 */
int plugin_exists (char *type);

/*
 * NAME
 *  plugin_load
 *
 * DESCRIPTION
 *  Searches the current `plugindir' (see `plugin_set_dir') for the plugin
 *  named $type and loads it. Afterwards the plugin's `module_register'
 *  function is called, which then calls `plugin_register' to register callback
 *  functions.
 *
 * ARGUMENTS
 *  `type'      Name of the plugin to load.
 *
 * RETURN VALUE
 *  Returns zero upon success, a value greater than zero if no plugin was found
 *  and a value below zero if an error occurs.
 *
 * NOTES
 *  No attempt is made to re-load an already loaded module.
 */
int  plugin_load (const char *type);

int  plugin_load_all (char *dir);
void plugin_init_all (void);
void plugin_read_all (void);

void plugin_register (char *type,
		void (*init) (void),
		void (*read) (void),
		void (*write) (char *, char *, char *));

#ifdef HAVE_LIBRRD
void plugin_write    (char *host, char *type, char *inst, char *val);
#endif /* HAVE_LIBRRD */
void plugin_submit   (char *type, char *inst, char *val);

#endif /* PLUGIN_H */
