#ifndef UWATT_UWATT_H_
#define UWATT_UWATT_H_

/*
 * Checkpoint 0 declares the target-side API surface. Checkpoint 2 supplies the
 * transport implementation and Zephyr integration.
 */

#ifdef CONFIG_UWATT
void uwatt_event(const char *name);
void uwatt_region_begin(const char *name);
void uwatt_region_end(const char *name);
void uwatt_state(const char *name);
#define UWATT_EVENT(name) uwatt_event(name)
#define UWATT_REGION_BEGIN(name) uwatt_region_begin(name)
#define UWATT_REGION_END(name) uwatt_region_end(name)
#define UWATT_STATE(name) uwatt_state(name)
#else
#define UWATT_EVENT(name) ((void)0)
#define UWATT_REGION_BEGIN(name) ((void)0)
#define UWATT_REGION_END(name) ((void)0)
#define UWATT_STATE(name) ((void)0)
#endif

#endif /* UWATT_UWATT_H_ */

