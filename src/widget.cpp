// widget.cpp
/*
  neogfx C++ GUI Library
  Copyright(C) 2016 Leigh Johnston
  
  This program is free software: you can redistribute it and / or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
  
  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "neogfx.hpp"
#include "app.hpp"
#include "widget.hpp"
#include "i_layout.hpp"

namespace neogfx
{
	widget::device_metrics_forwarder::device_metrics_forwarder(widget& aOwner) :
		iOwner(aOwner)
	{
	}

	size widget::device_metrics_forwarder::extents() const
	{
		return iOwner.iSize;
	}

	dimension widget::device_metrics_forwarder::horizontal_dpi() const
	{
		return iOwner.surface().horizontal_dpi();
	}

	dimension widget::device_metrics_forwarder::vertical_dpi() const
	{
		return iOwner.surface().vertical_dpi();
	}

	dimension widget::device_metrics_forwarder::em_size() const
	{
		return static_cast<dimension>(iOwner.font().size() / 72.0 * horizontal_dpi());
	}

	widget::widget() :
		iParent(0),
		iDeviceMetricsForwarder(*this),
		iUnitsContext(iDeviceMetricsForwarder),
		iMinimumSize{},
		iMaximumSize{},
		iVisible(true),
		iEnabled(true),
		iFocusPolicy(focus_policy::NoFocus),
		iTabBefore(0),
		iTabAfter(0),
		iForegroundColour{},
		iBackgroundColour{},
		iIgnoreMouseEvents(false)
	{
	}
	
	widget::widget(i_widget& aParent) :
		iParent(&aParent),
		iDeviceMetricsForwarder(*this),
		iUnitsContext(iDeviceMetricsForwarder),
		iMinimumSize{},
		iMaximumSize{},
		iVisible(true),
		iEnabled(true),
		iFocusPolicy(focus_policy::NoFocus),
		iTabBefore(0),
		iTabAfter(0),
		iForegroundColour{},
		iBackgroundColour{},
		iIgnoreMouseEvents(false)
	{
		aParent.add_widget(*this);
	}

	widget::widget(i_layout& aLayout) :
		iParent(0),
		iDeviceMetricsForwarder(*this),
		iUnitsContext(iDeviceMetricsForwarder),
		iMinimumSize{},
		iMaximumSize{},
		iVisible(true),
		iEnabled(true),
		iFocusPolicy(focus_policy::NoFocus),
		iTabBefore(0),
		iTabAfter(0),
		iForegroundColour{},
		iBackgroundColour{},
		iIgnoreMouseEvents(false)
	{
		aLayout.add_widget(*this);
	}

	widget::~widget()
	{
		if (has_parent())
			parent().remove_widget(*this);
	}

	const i_device_metrics& widget::device_metrics() const
	{
		return iDeviceMetricsForwarder;
	}

	units_e widget::units() const
	{
		return iUnitsContext.units();
	}

	units_e widget::set_units(units_e aUnits) const
	{
		return iUnitsContext.set_units(aUnits);
	}

	bool widget::is_root() const
	{
		return false;
	}

	void widget::set_parent(i_widget& aParent)
	{
		bool onSurface = has_surface();
		if (onSurface && &surface() != &aParent.surface())
		{
			surface().widget_removed(*this);
			onSurface = false;
		}
		iParent = &aParent;
		if (!onSurface && has_surface())
			surface().widget_added(*this);
	}
	
	bool widget::has_parent() const
	{
		return iParent != 0;
	}

	const i_widget& widget::parent() const
	{
		if (!has_parent())
			throw no_parent();
		return *iParent;
	}

	i_widget& widget::parent()
	{
		if (!has_parent())
			throw no_parent();
		return *iParent;
	}

	const i_widget& widget::ultimate_ancestor() const
	{
		const i_widget* w = this;
		while (w->has_parent())
			w = &w->parent();
		return *w;
	}

	i_widget& widget::ultimate_ancestor()
	{
		i_widget* w = this;
		while (w->has_parent())
			w = &w->parent();
			return *w;
	}

	bool widget::is_ancestor(const i_widget& aWidget) const
	{
		const i_widget* parent = &aWidget;
		while (parent->has_parent())
		{
			parent = &parent->parent();
			if (parent == this)
				return true;
		}
		return false;
	}

	void widget::add_widget(i_widget& aWidget)
	{
		iChildren.push_back(std::shared_ptr<i_widget>(std::shared_ptr<i_widget>(), &aWidget));
		aWidget.set_parent(*this);
		if (has_surface())
			surface().widget_added(aWidget);
	}

	void widget::add_widget(std::shared_ptr<i_widget> aWidget)
	{
		iChildren.push_back(aWidget);
		aWidget->set_parent(*this);
		if (has_surface())
			surface().widget_added(*aWidget);
	}

	void widget::remove_widget(i_widget& aWidget)
	{
		for (auto i = iChildren.begin(); i != iChildren.end(); ++i)
			if (&**i == &aWidget)
			{
				iChildren.erase(i);
				break;
			}
		if (has_surface())
			surface().widget_removed(aWidget);
	}

	const widget::widget_list& widget::children() const
	{
		return iChildren;
	}

	bool widget::has_surface() const
	{
		if (has_parent())
			return parent().has_surface();
		return false;
	}

	const i_surface& widget::surface() const
	{
		if (has_parent())
			return parent().surface();
		throw no_parent();
	}

	i_surface& widget::surface()
	{
		if (has_parent())
			return parent().surface();
		throw no_parent();
	}

	bool widget::has_layout() const
	{
		return iLayout.get() != 0;
	}

	void widget::set_layout(i_layout& aLayout)
	{
		iLayout = std::shared_ptr<i_layout>(std::shared_ptr<i_layout>(), &aLayout);
		iLayout->set_owner(this);
		for (auto& c : iChildren)
			iLayout->add_widget(c);
	}

	void widget::set_layout(std::shared_ptr<i_layout> aLayout)
	{
		iLayout = aLayout;
		iLayout->set_owner(this);
		for (auto& c : iChildren)
			iLayout->add_widget(c);
	}

	const i_layout& widget::layout() const
	{
		if (!iLayout)
			throw no_layout();
		return *iLayout;
	}
	
	i_layout& widget::layout()
	{
		if (!iLayout)
			throw no_layout();
		return *iLayout;
	}

	bool widget::can_defer_layout() const
	{
		return false;
	}

	bool widget::has_managing_layout() const
	{
		const i_widget* w = this;
		while (w->has_parent())
		{
			w = &w->parent();
			if (w->is_managing_layout())
				return true;
		}
		return false;
	}

	const i_widget& widget::managing_layout() const
	{
		const i_widget* w = this;
		while (w->has_parent())
		{
			w = &w->parent();
			if (w->is_managing_layout())
				return *w;
		}
		throw no_managing_layout();
	}

	i_widget& widget::managing_layout()
	{
		return const_cast<i_widget&>(const_cast<const widget*>(this)->managing_layout());
	}

	bool widget::is_managing_layout() const
	{
		return false;
	}

	void widget::layout_items(bool aDefer)
	{
		if (!aDefer)
		{
			if (has_layout())
				layout().layout_items(client_rect(false).top_left(), client_rect(false).extents());
		}
		else if (can_defer_layout())
		{
			if (!iLayoutTimer)
			{
				iLayoutTimer = std::unique_ptr<neolib::callback_timer>(new neolib::callback_timer(app::instance(), [this](neolib::callback_timer&)
				{
					widget::layout_items();
					iLayoutTimer.reset();
				}, 40));
			}
		}
		else if (has_managing_layout())
		{
			throw widget_cannot_defer_layout();
		}
	}

	void widget::layout_items_completed()
	{
		update();
	}

	point widget::position() const
	{
		return units_converter(*this).from_device_units(iPosition);
	}

	point widget::origin(bool aNonClient) const
	{
		if (has_parent())
			return position() + parent().origin(false);
		else
			return point{};
	}

	void widget::move(const point& aPosition)
	{
		if (iPosition != units_converter(*this).to_device_units(aPosition))
		{
			update();
			iPosition = units_converter(*this).to_device_units(aPosition);
			update();
			moved();
		}
	}

	void widget::moved()
	{
		layout_items();
	}
	
	size widget::extents() const
	{
		return units_converter(*this).from_device_units(iSize);
	}

	void widget::resize(const size& aSize)
	{
		if (iSize != units_converter(*this).to_device_units(aSize))
		{
			update();
			iSize = units_converter(*this).to_device_units(aSize);
			update();
			resized();
		}
	}

	void widget::resized()
	{
		layout_items();
	}

	rect widget::window_rect() const
	{
		return rect{origin(true), extents()};
	}

	rect widget::client_rect(bool aIncludeMargins) const
	{
		if (!aIncludeMargins)
			return rect{ margins().top_left(), extents() - margins().size() };
		else
			return rect{ point{}, extents() };
	}

	i_widget& widget::widget_at(const point& aPosition)
	{
		if (client_rect().contains(aPosition))
		{
			for (const auto& c : children())
				if (c->visible() && rect(c->position(), c->extents()).contains(aPosition))
					return c->widget_at(aPosition - c->position());
		}
		return *this;
	}

	bool widget::has_minimum_size() const
	{
		return iMinimumSize != boost::none;
	}

	size widget::minimum_size() const
	{
		return has_minimum_size() ?
			units_converter(*this).from_device_units(*iMinimumSize) :
			has_layout() ? 
				layout().minimum_size() + margins().size() : 
				size{};
	}

	void widget::set_minimum_size(const optional_size& aMinimumSize, bool aUpdateLayout)
	{
		if ((iMinimumSize == boost::none && aMinimumSize != boost::none) || 
			(iMinimumSize != boost::none && aMinimumSize == boost::none) ||
			(iMinimumSize != boost::none && *iMinimumSize != units_converter(*this).to_device_units(*aMinimumSize)))
		{
			iMinimumSize = aMinimumSize != boost::none ? units_converter(*this).to_device_units(*aMinimumSize) : optional_size();
			if (aUpdateLayout && has_managing_layout())
				managing_layout().layout_items(true);
		}
	}

	bool widget::has_maximum_size() const
	{
		return iMaximumSize != boost::none;
	}

	size widget::maximum_size() const
	{
		return has_maximum_size() ?
			units_converter(*this).from_device_units(*iMaximumSize) :
			has_layout() ?
				layout().maximum_size() : 
				size(std::numeric_limits<size::dimension_type>::max(), std::numeric_limits<size::dimension_type>::max());
	}

	void widget::set_maximum_size(const optional_size& aMaximumSize, bool aUpdateLayout)
	{
		if ((iMaximumSize == boost::none && aMaximumSize != boost::none) ||
			(iMaximumSize != boost::none && aMaximumSize == boost::none) ||
			(iMaximumSize != boost::none && *iMaximumSize != units_converter(*this).to_device_units(*aMaximumSize)))
		{
			iMaximumSize = aMaximumSize != boost::none ? units_converter(*this).to_device_units(*aMaximumSize) : optional_size();
			if (aUpdateLayout && has_managing_layout())
				managing_layout().layout_items(true);
		}
	}

	bool widget::is_fixed_size() const
	{
		return has_minimum_size() && minimum_size() == maximum_size();
	}

	void widget::set_fixed_size(const optional_size& aFixedSize, bool aUpdateLayout)
	{
		set_minimum_size(aFixedSize, aUpdateLayout);
		set_maximum_size(aFixedSize, aUpdateLayout);
	}

	size widget::size_hint() const
	{
		return size{};
	}

	bool widget::has_margins() const
	{
		return iMargins != boost::none;
	}

	margins widget::margins() const
	{
		return units_converter(*this).from_device_units(has_margins() ? *iMargins : app::instance().current_style().margins());
	}

	void widget::set_margins(const optional_margins& aMargins)
	{
		optional_margins oldMargins = iMargins;
		iMargins = (aMargins != boost::none ? units_converter(*this).to_device_units(*aMargins) : optional_margins());
		if (iMargins != oldMargins && has_managing_layout())
			managing_layout().layout_items(true);
	}

	void widget::update(bool aIncludeNonClient)
	{
		if (surface().destroyed())
			return;
		update(aIncludeNonClient ? window_rect() - origin() - client_rect().top_left() : client_rect());
	}

	void widget::update(const rect& aUpdateRect)
	{
		if (surface().destroyed()) 
			return;
		if (!visible())
			return;
		if (std::find(iUpdateRects.begin(), iUpdateRects.end(), aUpdateRect) == iUpdateRects.end())
		{
			iUpdateRects.push_back(aUpdateRect);
			if ((iBackgroundColour == boost::none || iBackgroundColour->alpha() != 0xFF) && has_parent() && has_surface() && &parent().surface() == &surface())
				parent().update(rect(aUpdateRect.position() + position() + (origin() - origin(true)), aUpdateRect.extents()));
			else if (is_root())
				surface().invalidate_surface(aUpdateRect);
			for (auto& c : iChildren)
			{
				if (!c->visible())
					continue;
				rect rectChild(c->position(), c->extents());
				rect intersection = aUpdateRect.intersection(rectChild);
				if (!intersection.empty())
					c->update();
			}
		}
	}

	bool widget::requires_update() const
	{
		if (!surface().native_surface().using_frame_buffer())
			return true;
		else
			return !iUpdateRects.empty();
	}

	rect widget::update_rect() const
	{
		if (iUpdateRects.empty())
			throw no_update_rect();
		rect result = iUpdateRects[0];
		for (const auto& ur : iUpdateRects)
			result = result.combine(ur);
		return result;
	}

	rect widget::default_clip_rect(bool aIncludeNonClient) const
	{
		rect clipRect = window_rect();
		clipRect = clipRect - origin(aIncludeNonClient);
		if (!aIncludeNonClient)
			clipRect = clipRect.intersection(client_rect());
		if (has_parent() && !is_root())
			clipRect = clipRect.intersection(parent().default_clip_rect() - point(origin(aIncludeNonClient) - parent().origin()));
		return clipRect;
	}

	void widget::render(graphics_context& aGraphicsContext) const
	{
		if (hidden())
		{
			iUpdateRects.clear();
			return;
		}
		if (requires_update())
		{
			aGraphicsContext.set_extents(extents());
			aGraphicsContext.set_origin(origin(true));
			aGraphicsContext.scissor_on(default_clip_rect(true));
			paint_non_client(aGraphicsContext);
			aGraphicsContext.scissor_off();
			aGraphicsContext.set_extents(client_rect().extents());
			aGraphicsContext.set_origin(origin() + client_rect().position());
			aGraphicsContext.scissor_on(default_clip_rect());
			paint(aGraphicsContext);
			aGraphicsContext.scissor_off();
		}
		iUpdateRects.clear();
		for (auto& c : iChildren)
		{
			rect rectChild(c->position(), c->extents());
			rect intersection = client_rect().intersection(rectChild);
			if (!intersection.empty())
				c->render(aGraphicsContext);
		}
	}

	bool widget::transparent_background() const
	{
		return !is_root();
	}

	void widget::paint_non_client(graphics_context& aGraphicsContext) const
	{
		if (has_background_colour() || !transparent_background())
		{
			if (surface().native_surface().using_frame_buffer())
				for (const auto& ur : iUpdateRects)
					aGraphicsContext.fill_solid_rect(ur, background_colour());
			else
				aGraphicsContext.fill_solid_rect(client_rect(), background_colour());
		}
	}

	void widget::paint(graphics_context& aGraphicsContext) const
	{
	}

	bool widget::has_foreground_colour() const
	{
		return iForegroundColour != boost::none;
	}

	colour widget::foreground_colour() const
	{
		if (has_foreground_colour())
			return *iForegroundColour;
		else
			return app::instance().current_style().foreground_colour();
	}

	void widget::set_foreground_colour(const optional_colour& aForegroundColour)
	{
		iForegroundColour = aForegroundColour;
		update();
	}

	bool widget::has_background_colour() const
	{
		return iBackgroundColour != boost::none;
	}

	colour widget::background_colour() const
	{
		if (has_background_colour())
			return *iBackgroundColour;
		else
			return app::instance().current_style().background_colour();
	}

	void widget::set_background_colour(const optional_colour& aBackgroundColour)
	{
		iBackgroundColour = aBackgroundColour;
		update();
	}

	colour widget::container_background_colour() const
	{
		const i_widget* w = this;
		while (w->transparent_background() && w->has_parent())
			w = &w->parent();
		if (!w->transparent_background() && w->has_background_colour())
			return w->background_colour();
		else
			return app::instance().current_style().colour();
	}

	bool widget::has_font() const
	{
		return iFont != boost::none;
	}

	const font& widget::font() const
	{
		if (has_font())
			return *iFont;
		else
			return app::instance().current_style().font();
	}

	void widget::set_font(const optional_font& aFont)
	{
		iFont = aFont;
		update();
	}

	bool widget::visible() const
	{
		return iVisible;
	}

	bool widget::hidden() const
	{
		return !visible();
	}

	void widget::show(bool aVisible)
	{
		if (iVisible != aVisible)
		{
			iVisible = aVisible;
			managing_layout().layout_items(true);
		}
	}

	void widget::show()
	{
		show(true);
	}

	void widget::hide()
	{
		show(false);
	}

	bool widget::enabled() const
	{
		return iEnabled;
	}
	
	bool widget::disabled() const
	{
		return !enabled();
	}

	void widget::enable(bool aEnable)
	{
		if (iEnabled != aEnable)
		{
			iEnabled = aEnable;
			update();
		}
	}

	void widget::enable()
	{
		enable(true);
	}

	void widget::disable()
	{
		enable(false);
	}

	bool widget::entered() const
	{
		return surface().has_entered_widget() && &surface().entered_widget() == this;
	}

	bool widget::capturing() const
	{
		return surface().has_capturing_widget() && &surface().capturing_widget() == this;
	}

	void widget::set_capture()
	{
		surface().set_capture(*this);
	}

	void widget::release_capture()
	{
		surface().release_capture(*this);
	}

	void widget::captured()
	{
	}

	void widget::released()
	{
	}

	focus_policy widget::focus_policy() const
	{
		return iFocusPolicy;
	}

	void widget::set_focus_policy(neogfx::focus_policy aFocusPolicy)
	{
		iFocusPolicy = aFocusPolicy;
	}

	bool widget::has_focus() const
	{
		return surface().has_focused_widget() && &surface().focused_widget() == this;
	}

	void widget::set_focus()
	{
		surface().set_focused_widget(*this);
	}

	void widget::release_focus()
	{
		surface().release_focused_widget(*this);
	}

	void widget::focus_gained()
	{
		update();
	}

	void widget::focus_lost()
	{
		update();
	}

	bool widget::has_tab_before() const
	{
		return iTabBefore != 0;
	}

	i_widget& widget::tab_before()
	{
		return *iTabBefore;
	}

	void widget::set_tab_before(i_widget& aWidget)
	{
		iTabBefore = &aWidget;
	}

	void widget::unset_tab_before()
	{
		iTabBefore = 0;
	}

	bool widget::has_tab_after() const
	{
		return iTabAfter != 0;
	}

	i_widget& widget::tab_after()
	{
		return *iTabAfter;
	}

	void widget::set_tab_after(i_widget& aWidget)
	{
		iTabAfter = &aWidget;
	}

	void widget::unset_tab_after()
	{
		iTabAfter = 0;
	}

	bool widget::ignore_mouse_events() const
	{
		return iIgnoreMouseEvents;
	}

	void widget::set_ignore_mouse_events(bool aIgnoreMouseEvents)
	{
		iIgnoreMouseEvents = aIgnoreMouseEvents;
	}

	void widget::mouse_wheel_scrolled(mouse_wheel aWheel, delta aDelta)
	{
		if (has_parent())
			parent().mouse_wheel_scrolled(aWheel, aDelta);
	}

	void widget::mouse_button_pressed(mouse_button aButton, const point& aPosition)
	{
		if (aButton == mouse_button::Middle && has_parent())
			parent().mouse_button_pressed(aButton, aPosition + position());
		else
		{
			set_capture();
			update();
		}
	}

	void widget::mouse_button_double_clicked(mouse_button aButton, const point& aPosition)
	{
	}

	void widget::mouse_button_released(mouse_button aButton, const point& aPosition)
	{
		if (capturing())
			release_capture();
		update();
	}

	void widget::mouse_moved(const point& aPosition)
	{
	}

	void widget::mouse_entered()
	{
	}

	void widget::mouse_left()
	{
	}

	void widget::key_pressed(scan_code_e aScanCode, key_code_e aKeyCode, key_modifiers_e aKeyModifiers)
	{
	}

	void widget::key_released(scan_code_e aScanCode, key_code_e aKeyCode, key_modifiers_e aKeyModifiers)
	{
	}

	void widget::text_input(const std::string& aText)
	{
	}

	i_widget& widget::widget_for_mouse_event(const point& aPosition)
	{
		if (client_rect().contains(aPosition))
		{
			i_widget* w = &widget_at(aPosition);
			while (w != this && (w->hidden() || w->disabled() || w->ignore_mouse_events()))
			{
				w = &w->parent();
			}
			return *w;
		}
		else
			return *this;
	}

	graphics_context widget::create_graphics_context() const
	{
		return graphics_context(*this);
	}
}

