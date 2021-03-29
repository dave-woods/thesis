// Allens
export function equals(x, y) {
    return ['|' + x + ',' + y + '|']
}
export function before(x, y) {
    return ['|' + x + '||' + y + '|']
}
export function after(x, y) {
    return before(y, x)
}
export function meets(x, y) {
    return ['|' + x + '|' + y + '|']
}
export function meets_inv(x, y) {
    return meets(y, x)
}
export function starts(x, y) {
    return ['|' + x + ',' + y + '|' + y + '|']
}
export function starts_inv(x, y) {
    return starts(y, x)
}
export function finishes(x, y) {
    return ['|' + y + '|' + x + ',' + y + '|']
}
export function finishes_inv(x, y) {
    return finishes(y, x)
}
export function during(x, y) {
    return ['|' + y + '|' + x + ',' + y + '|' + y + '|']
}
export function during_inv(x, y) {
    return during(y, x)
}
export function overlaps(x, y) {
    return ['|' + x + '|' + x + ',' + y + '|' + y + '|']
}
export function overlaps_inv(x, y) {
    return overlaps(y, x)
}

// Freksa
export function older(x, y) {
    return [...fi(x,y), ...di(x,y), ...m(x,y), ...b(x,y), ...o(x,y)]
}
export function younger(x, y) {
    return [...older(y, x)]
}
export function head_to_head(x, y) {
    return [...s(x, y), ...si(x, y), ...e(x, y)]
}
export function tail_to_tail(x, y) {
    return [...f(x, y), ...fi(x, y), ...e(x, y)]
}
export function survived_by(x, y) {
    return [...b(x, y), ...m(x, y), ...o(x, y), ...s(x, y), ...d(x, y)]
}
export function survives(x, y) {
    return [...survived_by(y, x)]
}
export function precedes(x, y) {
    return [...b(x, y), ...m(x, y)]
}
export function succeeds(x, y) {
    return [...precedes(y, x)]
}
export function contemporary(x, y) {
    return [...o(x, y), ...fi(x, y), ...di(x, y), ...si(x, y), ...e(x, y), ...s(x, y), ...d(x, y), ...f(x, y), ...oi(x, y)]
}
export function born_before_death(x, y) {
    return [...precedes(x, y), ...contemporary(x, y)]
}
export function died_after_birth(x, y) {
    return [...born_before_death(y, x)]
}
export function older_survived_by(x, y) {
    return [...precedes(x, y), ...o(x, y)]
}
export function younger_survives(x, y) {
    return [...older_survived_by(y, x)]
}
export function older_contemporary(x, y) {
    return [...o(x, y), ...fi(x, y), ...di(x, y)]
}
export function younger_contemporary(x, y) {
    return [...older_contemporary(y, x)]
}
export function surviving_contemporary(x, y) {
    return [...di(x, y), ...si(x, y), ...oi(x, y)]
}
export function survived_by_contemporary(x, y) {
    return [...surviving_contemporary(y, x)]
}
export function unknown(x, y) {
    return [...precedes(x, y), ...contemporary(x, y), ...succeeds(x, y)]
}

// Mnemonics
export function e(x, y) {
    return equals(x, y)
}
export function b(x, y) {
    return before(x, y)
}
export function bi(x, y) {
    return after(x, y)
}
export function m(x, y) {
    return meets(x, y)
}
export function mi(x, y) {
    return meets_inv(x, y)
}
export function s(x, y) {
    return starts(x, y)
}
export function si(x, y) {
    return starts_inv(x, y)
}
export function f(x, y) {
    return finishes(x, y)
}
export function fi(x, y) {
    return finishes_inv(x, y)
}
export function d(x, y) {
    return during(x, y)
}
export function di(x, y) {
    return during_inv(x, y)
}
export function o(x, y) {
    return overlaps(x, y)
}
export function oi(x, y) {
    return overlaps_inv(x, y)
}

export function un(x, y) {
    return unknown(x, y)
}
export function ol(x, y) {
    return older(x, y)
}
export function hh(x, y) {
    return head_to_head(x, y)
}
export function yo(x, y) {
    return younger(x, y)
}
export function sb(x, y) {
    return survived_by(x, y)
}
export function tt(x, y) {
    return tail_to_tail(x, y)
}
export function sv(x, y) {
    return survives(x, y)
}
export function pr(x, y) {
    return precedes(x, y)
}
export function bd(x, y) {
    return born_before_death(x, y)
}
export function ct(x, y) {
    return contemporary(x, y)
}
export function db(x, y) {
    return died_after_birth(x, y)
}
export function sd(x, y) {
    return succeeds(x, y)
}
export function ob(x, y) {
    return older_survived_by(x, y)
}
export function oc(x, y) {
    return older_contemporary(x, y)
}
export function sc(x, y) {
    return surviving_contemporary(x, y)
}
export function bc(x, y) {
    return survived_by_contemporary(x, y)
}
export function yc(x, y) {
    return younger_contemporary(x, y)
}
export function ys(x, y) {
    return younger_survives(x, y)
}