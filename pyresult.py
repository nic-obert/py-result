from __future__ import annotations

from typing import Callable, Generic, TypeVar, NoReturn


def _raise(e: Exception) -> NoReturn:
    raise e


T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")


class Option(Generic[T]):

    """
        Type Option represents an optional value: every Option is either Some and contains a value, or Null, and does not.
    """

    __slots__ = ("_value",)


    def __init__(self, value: T | None) -> None:
        self._value = value
    
    
    def is_some(self) -> bool:
        """
            Returns true if the option is a Some value.
        """

        return self._value is not None
    

    def is_null(self) -> bool:
        """
            Returns true if the option is a Null value.
        """

        return self._value is None
    

    def unwrap(self) -> T:
        """
            Returns the contained value or raises an exception if the value is a Null.
        """

        if self.is_some():
            value = self._value
            self._value = None
            return value
        
        raise Exception("Called unwrap on a null value")
    
    
    def unwrap_or(self, default: T) -> T:
        """
            Returns the contained value or a default.
        """

        if self.is_some():
            value = self._value
            self._value = None
            return value
        
        return default
    

    def unwrap_or_else(self, default: Callable[[], T]) -> T:
        """
            Returns the contained value or computes it from a closure.
        """

        if self.is_some():
            value = self._value
            self._value = None
            return value
        
        return default()
    

    def unwrap_unchecked(self) -> T:
        """
            Returns the contained value without checking if it is a Null.
        """

        value = self._value
        self._value = None
        return value
    

    def map(self, func: Callable[[T], U]) -> Option[U]:
        """
            Maps an Option<T> to Option<U> by applying a function to a contained value (if Some), or returns Null (if Null).
        """

        if self.is_some():
            return Some[T](func(self._value))
        
        return Null[T]()
    

    def map_or(self, default: U, func: Callable[[T], U]) -> U:
        """
            Applies a function to the contained value (if Some), or returns a default (if Null).
        """

        if self.is_some():
            return func(self._value)
        
        return default
    

    def map_or_else(self, default: Callable[[], U], func: Callable[[T], U]) -> U:
        """
            Applies a function to the contained value (if Some), or computes a default (if Null).
        """

        if self.is_some():
            return func(self._value)
        
        return default()
    

    def replace(self, value: T) -> Option[T]:
        """
            Replaces the actual value in the option by the specified one, returning the old value if present, leaving a Null in its place.
        """

        ret = self._value
        self._value = value

        if ret is None:
            return Null[T]()
        return Some[T](ret)
    

    def take(self) -> Option[T]:
        """
            Takes the value out of the option, leaving a Null in its place.
        """

        return self.replace(None)
    

    def expect(self, msg: str) -> T:
        """
            Returns the contained value or raises an exception if the value is a Null with a custom message provided by msg.
        """
        
        return self.unwrap_or_else(lambda: _raise(Exception(msg)))
    

    def iter(self) -> Option[T]:
        """
            Returns an iterator over the possibly contained value.
        """

        if self.is_some():
            yield Some[T](self._value)

        yield Null[T]()


class Some(Generic[T]):
    """
        The Some variant of Option<T>.
    """

    __slots__ = ()

    def __new__(cls, value: T) -> Option[T]:
        return Option[T](value)

    
class Null(Generic[T]):
    """
        The Null variant of Option<T>.
    """

    __slots__ = ()

    def __new__(cls) -> Option[T]:
        return Option[T](None)
    

class Result(Generic[T, E]):

    """
        Type Result represents either success (Ok) or failure (Err).
    """

    class _Ok(Generic[T]):

        __slots__ = ("value",)

        def __init__(self, value: T) -> None:
            self.value = value

        
        def __call__(self) -> T:
            return self.value


    class _Err(Generic[E]):
            
        __slots__ = ("error",)

        def __init__(self, error: E) -> None:
            self.error = error

        
        def __call__(self) -> E:
            return self.error
        

    __slots__ = ("value",)

    def __init__(self, value: _Ok[T] | _Err[E]) -> None:
        self.value = value

    
    def is_ok(self) -> bool:
        """
            Returns true if the result is Ok.
        """

        return isinstance(self.value, self._Ok[T])
    

    def is_err(self) -> bool:
        """
            Returns true if the result is Err.
        """

        return isinstance(self.value, self._Err[E])
    

    def ok(self) -> Option[T]:
        """
            Converts from Result<T, E> to Option<T>.
        """

        if self.is_ok():
            return Some[T](self.value())
        
        return Null[T]()
    

    def err(self) -> Option[E]:
        """
            Converts from Result<T, E> to Option<E>.
        """
        
        if self.is_err():
            return Some[T](self.value())
        
        return Null[T]()
    

    def expect(self, msg: str) -> T:
        """
            Returns the contained Ok value or raises an exception if the value is an Err with a custom message provided by msg.
        """

        if self.is_ok():
            return self.value()
        
        raise Exception(msg)
    

    def iter(self) -> Result[T, E]:
        """
            Returns an iterator over the possibly contained value.
        """

        if self.is_ok():
            yield Some[T](self.value())
        
        yield Null[T]()

    
    def unwrap(self) -> T:
        """
            Returns the contained Ok value or raises an exception if the value is an Err.
        """

        if self.is_ok():
            value = self.value()
            self.value = None
            return value
        
        raise Exception(self.value())
    

    def unwrap_or(self, default: T) -> T:
        """
            Returns the contained Ok value or a default.
        """

        if self.is_ok():
            value = self.value()
            self.value = None
            return value
        
        return default
    

    def unwrap_or_else(self, default: Callable[[E], T]) -> T:
        """
            Returns the contained Ok value or computes it from a closure.
        """

        if self.is_ok():
            value = self.value()
            self.value = None
            return value
        
        return default(self.value())
    

    def unwrap_unchecked(self) -> T:
        """
            Returns the contained Ok value without checking if it is an Err.
        """

        value = self.value()
        self.value = None
        return value
    

    def unwrap_err(self) -> E:
        """
            Returns the contained Err value or raises an exception if the value is an Ok.
        """

        if self.is_err():
            error = self.value()
            self.value = None
            return error
        
        raise Exception(self.value())
    

    def unwrap_err_unchecked(self) -> E:
        """
            Returns the contained Err value without checking if it is an Ok.
        """

        error = self.value()
        self.value = None
        return error
    

class Ok(Generic[T]):

    """
        The Ok variant of Result<T, E>.
    """

    __slots__ = ()

    def __new__(cls, value: T) -> Result[T, E]:
        return Result[T, E](Result._Ok[T](value))


class Err(Generic[E]):

    """
        The Err variant of Result<T, E>.
    """

    __slots__ = ()

    def __new__(cls, error: E) -> Result[T, E]:
        return Result[T, E](Result._Err[E](error))
    
